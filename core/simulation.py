"""Motor de la simulación. Único módulo del core que usa Qt (QObject, QTimer, Signal)."""
import random

from PySide6.QtCore import QObject, QTimer, Signal

from utils import colors

from . import config, scheduler
from .process import Proceso
from .states import Estado
from .timeline import LineaTiempo


class Simulation(QObject):
    tick = Signal(int)          # nuevo valor del reloj (ms)
    cambio = Signal()           # cambió alguna cola o proceso -> refrescar paneles
    segmento = Signal(object)   # segmento del Gantt creado o extendido
    evento = Signal(str)        # línea para el registro de eventos
    reiniciado = Signal()

    def __init__(self, parent=None, seed=None):
        super().__init__(parent)
        self._rng = random.Random(seed)
        self.rata = config.RATA_POR_DEFECTO
        self.linea = LineaTiempo()
        self._timer = QTimer(self)
        self._timer.setInterval(config.TICK_REAL_MS)
        self._timer.timeout.connect(self.paso)
        self._limpiar()

    # ---------- estado ----------
    def _limpiar(self):
        self.reloj = 0
        self._siguiente_pid = config.PID_INICIAL
        self._contador_cola = 0
        self.procesos: dict[int, Proceso] = {}
        self.preparados: list[Proceso] = []
        self.suspendidos: list[Proceso] = []
        self.terminados: list[Proceso] = []
        self.en_cpu: Proceso | None = None

    @property
    def corriendo(self) -> bool:
        return self._timer.isActive()

    def buscar(self, pid: int) -> Proceso | None:
        return self.procesos.get(pid)

    # ---------- controles ----------
    def iniciar(self):
        self._timer.start()

    def pausar(self):
        self._timer.stop()

    def reiniciar(self):
        self.pausar()
        self._limpiar()
        self.linea.limpiar()
        self.reiniciado.emit()
        self.tick.emit(0)
        self.cambio.emit()
        self.evento.emit("Simulación reiniciada.")

    def set_velocidad(self, ms_reales: int):
        self._timer.setInterval(ms_reales)

    def set_rata(self, rata: int):
        self.rata = rata
        for p in self.procesos.values():
            if p.estado is not Estado.TERMINADO:
                p.quantum = scheduler.calcular_quantum(p.tiempo_total, rata)
        self._log(f"Rata de quantum = {rata}. Quantums recalculados.")
        self.cambio.emit()

    # ---------- procesos ----------
    def agregar_proceso(self, nombre="", prioridad=3, tiempo_total=None, interactividad=None) -> Proceso:
        pid = self._siguiente_pid
        self._siguiente_pid += 1
        indice = pid - config.PID_INICIAL
        nombre = nombre.strip() or f"Proceso {self._letra(indice)}"
        prioridad = max(config.PRIORIDAD_MIN, min(config.PRIORIDAD_MAX, int(prioridad)))
        if tiempo_total is None:
            tiempo_total = self._multiplo(*config.TIEMPO_TOTAL_RANGO)
        if interactividad is None:
            interactividad = self._rng.randint(*config.INTERACTIVIDAD_RANGO)

        p = Proceso(
            pid=pid, nombre=nombre, prioridad=prioridad, tiempo_total=tiempo_total,
            quantum=scheduler.calcular_quantum(tiempo_total, self.rata),
            color=colors.color_proceso(indice), interactividad=interactividad,
        )
        self.procesos[pid] = p
        self._log(f"{p.nombre} (PID {p.pid}) creado. Prioridad {p.prioridad}, quantum {p.quantum} ms.")
        self._a_preparados(p)
        if self.en_cpu is None:
            self._despachar()
        self.cambio.emit()
        return p

    @staticmethod
    def _letra(indice: int) -> str:
        letra = chr(ord("A") + indice % 26)
        return letra + (str(indice // 26) if indice >= 26 else "")

    def _multiplo(self, lo: int, hi: int) -> int:
        return self._rng.randrange(lo, hi + 1, config.TICK_MS)

    # ---------- ciclo ----------
    def paso(self):
        self.reloj += config.TICK_MS

        # 1. Suspendidos avanzan su E/S
        for p in list(self.suspendidos):
            p.bloqueo_restante -= config.TICK_MS
            if p.bloqueo_restante <= 0:
                self.suspendidos.remove(p)
                self._log(f"{p.nombre} termina su E/S.")
                self._a_preparados(p)

        # 2. Preparados esperan
        for p in self.preparados:
            p.tiempo_espera += config.TICK_MS

        # 3. Proceso en CPU
        p = self.en_cpu
        if p:
            p.tiempo_ejecutado += config.TICK_MS
            p.quantum_usado += config.TICK_MS
            self.linea.extender(self.reloj)
            self.segmento.emit(self.linea.abierto)
            if p.tiempo_ejecutado >= p.tiempo_total:
                self._terminar(p)
            elif p.bloqueo_en is not None and p.quantum_usado >= p.bloqueo_en:
                self._bloquear(p)
            elif p.quantum_usado >= p.quantum:
                self._expropiar(p)

        # 4. CPU libre -> planificador
        if self.en_cpu is None:
            self._despachar()

        self.tick.emit(self.reloj)
        self.cambio.emit()

    def _a_preparados(self, p: Proceso):
        p.estado = Estado.PREPARADO
        self._contador_cola += 1
        p.orden_cola = self._contador_cola
        self.preparados.append(p)

    def _despachar(self):
        p = scheduler.elegir(self.preparados)
        if p is None:
            return
        razones = scheduler.explicar(p, self.preparados)
        self.preparados.remove(p)
        p.estado = Estado.EJECUCION
        p.quantum_usado = 0
        p.bloqueo_en = self._decidir_bloqueo(p)
        self.en_cpu = p
        self.segmento.emit(self.linea.abrir(p, self.reloj))
        self._log(f"{p.nombre} entra a CPU. " + " ".join(razones))

    def _decidir_bloqueo(self, p: Proceso):
        if p.quantum <= config.TICK_MS or self._rng.random() * 100 >= p.interactividad:
            return None
        return self._rng.randrange(config.TICK_MS, p.quantum, config.TICK_MS)

    def _terminar(self, p: Proceso):
        self.linea.cerrar()
        p.estado = Estado.TERMINADO
        self.terminados.append(p)
        self.en_cpu = None
        self._log(f"{p.nombre} terminó.")

    def _bloquear(self, p: Proceso):
        self.linea.cerrar()
        p.estado = Estado.SUSPENDIDO
        p.causa_bloqueo = self._rng.choice(config.CAUSAS_BLOQUEO)
        p.bloqueo_total = p.bloqueo_restante = self._multiplo(*config.BLOQUEO_DURACION_RANGO)
        p.bloqueo_en = None
        p.quantum_usado = 0
        self.suspendidos.append(p)
        self.en_cpu = None
        self._log(f"{p.nombre} se suspende: {p.causa_bloqueo} ({p.bloqueo_total} ms).")

    def _expropiar(self, p: Proceso):
        self.linea.cerrar()
        p.quantum_usado = 0
        self.en_cpu = None
        self._log(f"{p.nombre} agotó su quantum.")
        self._a_preparados(p)

    def _log(self, msg: str):
        self.evento.emit(f"[{self.reloj:>6} ms] {msg}")
