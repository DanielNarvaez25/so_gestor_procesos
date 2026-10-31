"""Reglas de simulación y tiempo virtual. No depende de Qt ni de la interfaz."""
import random

from . import configuracion as config, planificador as scheduler
from .proceso import Proceso
from .estados import Estado
from .linea_tiempo import LineaTiempo


class MotorSimulacion:
    def __init__(self, seed=None):
        self._rng = random.Random(seed)
        self.rata = config.RATA_POR_DEFECTO
        self.linea = LineaTiempo()
        self.eventos: list[str] = []
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
    def hay_trabajo(self) -> bool:
        return bool(self.en_cpu or self.preparados or self.suspendidos)

    def preparados_ordenados(self):
        return sorted(self.preparados, key=scheduler.clave_orden)

    def buscar(self, pid: int) -> Proceso | None:
        return self.procesos.get(pid)

    # ---------- controles ----------
    def reiniciar(self):
        self._limpiar()
        self.linea.limpiar()
        self.eventos.clear()
        self._log("Simulación reiniciada.")

    def extraer_eventos(self) -> list[str]:
        eventos, self.eventos = self.eventos, []
        return eventos

    def agregar_aleatorio(self, nombre=""):
        from .generador import datos_aleatorios
        return self.agregar_proceso(nombre, **datos_aleatorios(self._rng))

    def set_rata(self, rata: int):
        if rata not in config.RATAS_QUANTUM:
            raise ValueError("Rata de quantum no admitida")
        self.rata = rata
        # El turno en curso conserva su quantum y su E/S programada.
        for p in self.procesos.values():
            if p.estado not in (Estado.TERMINADO, Estado.EJECUCION):
                p.quantum = scheduler.calcular_quantum(p.tiempo_total, rata)
        self._log(f"Rata de quantum = {rata}. Se aplicará desde el próximo turno de CPU.")

    # ---------- procesos ----------
    def agregar_proceso(self, nombre="", prioridad=3, tiempo_total=None, interactividad=None) -> Proceso:
        if tiempo_total is not None and (not isinstance(tiempo_total, int) or isinstance(tiempo_total, bool) or tiempo_total <= 0):
            raise ValueError("El tiempo total debe ser un entero positivo")
        if interactividad is not None and (not isinstance(interactividad, int) or not 0 <= interactividad <= 100):
            raise ValueError("La interactividad debe estar entre 0 y 100")
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
            interactividad=interactividad,
        )
        self.procesos[pid] = p
        self._log(f"{p.nombre} (PID {p.pid}) creado. Prioridad {p.prioridad}, quantum {p.quantum} ms.")
        self._a_preparados(p)
        if self.en_cpu is None:
            self._despachar()
        return p

    @staticmethod
    def _letra(indice: int) -> str:
        letra = chr(ord("A") + indice % 26)
        return letra + (str(indice // 26) if indice >= 26 else "")

    def _multiplo(self, lo: int, hi: int) -> int:
        return self._rng.randrange(lo, hi + 1, config.TICK_MS)

    # ---------- ciclo ----------
    def paso(self):
        """Avanza un tick resolviendo los eventos en su instante exacto."""
        if self.en_cpu is None:
            self._despachar()
        limite = self.reloj + config.TICK_MS
        while self.reloj < limite and (self.en_cpu or self.preparados or self.suspendidos):
            p = self.en_cpu
            delta = limite - self.reloj
            if p is not None:
                delta = min(delta, p.tiempo_restante, p.quantum - p.quantum_usado)
                if p.bloqueo_en is not None:
                    delta = min(delta, p.bloqueo_en - p.quantum_usado)
            if self.suspendidos:
                delta = min(delta, min(q.bloqueo_restante for q in self.suspendidos))

            # Solo acumulan espera quienes estuvieron preparados en este intervalo.
            for q in self.preparados:
                q.tiempo_espera += delta
            for q in self.suspendidos:
                q.bloqueo_restante -= delta
            self.reloj += delta
            if p is not None:
                p.tiempo_ejecutado += delta
                p.quantum_usado += delta
                self.linea.extender(self.reloj)

            for q in list(self.suspendidos):
                if q.bloqueo_restante == 0:
                    self.suspendidos.remove(q)
                    self._log(f"{q.nombre} termina su E/S.")
                    self._a_preparados(q)
            if p is not None:
                if p.tiempo_restante == 0:
                    self._terminar(p)
                elif p.bloqueo_en is not None and p.quantum_usado >= p.bloqueo_en:
                    self._bloquear(p)
                elif p.quantum_usado >= p.quantum:
                    self._expropiar(p)
            if self.en_cpu is None:
                self._despachar()


    def _a_preparados(self, p: Proceso):
        p.estado = Estado.PREPARADO
        p.quantum = scheduler.calcular_quantum(p.tiempo_total, self.rata)
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
        p.quantum = scheduler.calcular_quantum(p.tiempo_total, self.rata)
        p.quantum_usado = 0
        p.bloqueo_en = self._decidir_bloqueo(p)
        self.en_cpu = p
        self.linea.abrir(p, self.reloj)
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
        self.eventos.append(f"[{self.reloj:>6} ms] {msg}")
