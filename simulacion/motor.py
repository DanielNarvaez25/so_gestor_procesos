"""Reglas de simulación y tiempo virtual. No depende de Qt ni de la interfaz."""
import random

from estructuras import ListaEnlazada

from . import configuracion, planificador
from .proceso import Proceso
from .estados import Estado
from .linea_tiempo import LineaTiempo


class MotorSimulacion:
    def __init__(self, seed=None):
        self._generador_aleatorio = random.Random(seed)
        self.divisor_quantum = configuracion.DIVISOR_QUANTUM_POR_DEFECTO
        self.linea = LineaTiempo()
        self.eventos: list[str] = []
        self._limpiar()

    # ---------- estado ----------
    def _limpiar(self):
        self.reloj = 0
        self._siguiente_pid = configuracion.PID_INICIAL
        self._contador_cola = 0
        self.procesos: dict[int, Proceso] = {}
        self.preparados: ListaEnlazada[Proceso] = ListaEnlazada()
        self.suspendidos: ListaEnlazada[Proceso] = ListaEnlazada()
        self.terminados: ListaEnlazada[Proceso] = ListaEnlazada()
        self.en_cpu: Proceso | None = None

    @property
    def hay_trabajo(self) -> bool:
        return bool(self.en_cpu or self.preparados or self.suspendidos)

    def preparados_ordenados(self):
        return sorted(self.preparados, key=planificador.clave_orden)

    def buscar(self, pid: int) -> Proceso | None:
        return self.procesos.get(pid)

    # ---------- controles ----------
    def reiniciar(self):
        self._limpiar()
        self.linea.limpiar()
        self.eventos.clear()
        self._registrar_evento("Simulación reiniciada.")

    def extraer_eventos(self) -> list[str]:
        eventos, self.eventos = self.eventos, []
        return eventos

    def agregar_aleatorio(self, nombre=""):
        from .generador import datos_aleatorios
        return self.agregar_proceso(nombre, **datos_aleatorios(self._generador_aleatorio))

    def cambiar_divisor_quantum(self, divisor_quantum: int):
        """Cambia el divisor del quantum para los próximos turnos de CPU."""
        if divisor_quantum not in configuracion.DIVISORES_QUANTUM:
            raise ValueError("Rata de quantum no admitida")
        self.divisor_quantum = divisor_quantum
        # El turno en curso conserva su quantum y su E/S programada.
        for proceso in self.procesos.values():
            if proceso.estado not in (Estado.TERMINADO, Estado.EJECUCION):
                proceso.quantum = planificador.calcular_quantum(proceso.tiempo_total, divisor_quantum)
        self._registrar_evento(f"Rata de quantum = {divisor_quantum}. Se aplicará desde el próximo turno de CPU.")

    # ---------- procesos ----------
    def agregar_proceso(self, nombre="", prioridad=3, tiempo_total=None, interactividad=None) -> Proceso:
        if tiempo_total is not None:
            tiempo_es_entero = isinstance(tiempo_total, int) and not isinstance(tiempo_total, bool)
            if not tiempo_es_entero or tiempo_total <= 0:
                raise ValueError("El tiempo total debe ser un entero positivo")
        if interactividad is not None:
            interactividad_es_entera = isinstance(interactividad, int)
            if not interactividad_es_entera or not 0 <= interactividad <= 100:
                raise ValueError("La interactividad debe estar entre 0 y 100")
        pid = self._siguiente_pid
        self._siguiente_pid += 1
        indice = pid - configuracion.PID_INICIAL
        nombre = nombre.strip() or f"Proceso {self._letra_del_proceso(indice)}"
        prioridad = max(configuracion.PRIORIDAD_MIN, min(configuracion.PRIORIDAD_MAX, int(prioridad)))
        if tiempo_total is None:
            tiempo_total = self._sortear_duracion_en_milisegundos(*configuracion.TIEMPO_TOTAL_RANGO)
        if interactividad is None:
            interactividad = self._generador_aleatorio.randint(*configuracion.INTERACTIVIDAD_RANGO)

        proceso = Proceso(
            pid=pid, nombre=nombre, prioridad=prioridad, tiempo_total=tiempo_total,
            quantum=planificador.calcular_quantum(tiempo_total, self.divisor_quantum),
            interactividad=interactividad,
        )
        self.procesos[pid] = proceso
        self._registrar_evento(f"{proceso.nombre} (PID {proceso.pid}) creado. Prioridad {proceso.prioridad}, quantum {proceso.quantum} ms.")
        self._agregar_a_preparados(proceso)
        if self.en_cpu is None:
            self._asignar_cpu_al_siguiente_proceso()
        return proceso

    @staticmethod
    def _letra_del_proceso(indice: int) -> str:
        letra = chr(ord("A") + indice % 26)
        return letra + (str(indice // 26) if indice >= 26 else "")

    def _sortear_duracion_en_milisegundos(self, minimo: int, maximo: int) -> int:
        return self._generador_aleatorio.randrange(minimo, maximo + 1, configuracion.TICK_MS)

    # ---------- ciclo de simulación ----------
    def paso(self):
        """Avanza hasta 10 ms, atendiendo cada cambio en su instante exacto.

        Un proceso puede terminar antes del fin del paso. En ese caso, el
        siguiente utiliza el tiempo sobrante; no se pierde tiempo de CPU.
        """
        if self.en_cpu is None:
            self._asignar_cpu_al_siguiente_proceso()
        fin_del_paso = self.reloj + configuracion.TICK_MS

        while self.reloj < fin_del_paso and self.hay_trabajo:
            tiempo_a_avanzar = self._tiempo_hasta_proximo_evento(fin_del_paso)
            self._avanzar_reloj_y_tiempos(tiempo_a_avanzar)
            self._reincorporar_procesos_con_entrada_salida_finalizada()
            self._resolver_estado_del_proceso_en_cpu()
            if self.en_cpu is None:
                self._asignar_cpu_al_siguiente_proceso()

    def _tiempo_hasta_proximo_evento(self, fin_del_paso: int) -> int:
        """Avanza solo hasta el primer evento: fin, quantum, E/S o fin del paso."""
        tiempo_disponible = fin_del_paso - self.reloj
        proceso_actual = self.en_cpu
        if proceso_actual is not None:
            quantum_restante = proceso_actual.quantum - proceso_actual.quantum_usado
            tiempo_disponible = min(
                tiempo_disponible, proceso_actual.tiempo_restante, quantum_restante
            )
            if proceso_actual.bloqueo_en is not None:
                tiempo_hasta_entrada_salida = (
                    proceso_actual.bloqueo_en - proceso_actual.quantum_usado
                )
                tiempo_disponible = min(tiempo_disponible, tiempo_hasta_entrada_salida)
        for proceso_suspendido in self.suspendidos:
            tiempo_disponible = min(tiempo_disponible, proceso_suspendido.bloqueo_restante)
        return tiempo_disponible

    def _avanzar_reloj_y_tiempos(self, tiempo_transcurrido: int) -> None:
        """Actualiza espera, E/S y ejecución durante el mismo intervalo."""
        for proceso_preparado in self.preparados:
            proceso_preparado.tiempo_espera += tiempo_transcurrido
        for proceso_suspendido in self.suspendidos:
            proceso_suspendido.bloqueo_restante -= tiempo_transcurrido
        self.reloj += tiempo_transcurrido
        if self.en_cpu is not None:
            self.en_cpu.tiempo_ejecutado += tiempo_transcurrido
            self.en_cpu.quantum_usado += tiempo_transcurrido
            self.linea.extender(self.reloj)

    def _reincorporar_procesos_con_entrada_salida_finalizada(self) -> None:
        """Devuelve a preparados todos los que terminaron su espera de E/S."""
        for proceso_suspendido in self.suspendidos:
            if proceso_suspendido.bloqueo_restante == 0:
                self.suspendidos.eliminar(proceso_suspendido)
                self._registrar_evento(f"{proceso_suspendido.nombre} termina su E/S.")
                self._agregar_a_preparados(proceso_suspendido)

    def _resolver_estado_del_proceso_en_cpu(self) -> None:
        """Comprueba las salidas de CPU en este orden: fin, E/S y quantum."""
        proceso_actual = self.en_cpu
        if proceso_actual is None:
            return
        if proceso_actual.tiempo_restante == 0:
            self._finalizar_proceso(proceso_actual)
        elif (proceso_actual.bloqueo_en is not None
              and proceso_actual.quantum_usado >= proceso_actual.bloqueo_en):
            self._suspender_por_entrada_salida(proceso_actual)
        elif proceso_actual.quantum_usado >= proceso_actual.quantum:
            self._devolver_por_quantum_agotado(proceso_actual)

    # ---------- movimientos entre estados ----------
    def _agregar_a_preparados(self, proceso: Proceso):
        proceso.estado = Estado.PREPARADO
        proceso.quantum = planificador.calcular_quantum(proceso.tiempo_total, self.divisor_quantum)
        self._contador_cola += 1
        proceso.orden_cola = self._contador_cola
        self.preparados.agregar(proceso)

    def _asignar_cpu_al_siguiente_proceso(self):
        proceso = planificador.seleccionar_siguiente_proceso(self.preparados)
        if proceso is None:
            return
        razones = planificador.explicar_seleccion(proceso, self.preparados)
        self.preparados.eliminar(proceso)
        proceso.estado = Estado.EJECUCION
        proceso.quantum = planificador.calcular_quantum(proceso.tiempo_total, self.divisor_quantum)
        proceso.quantum_usado = 0
        proceso.bloqueo_en = self._programar_solicitud_entrada_salida(proceso)
        self.en_cpu = proceso
        self.linea.abrir(proceso, self.reloj)
        self._registrar_evento(f"{proceso.nombre} entra a CPU. " + " ".join(razones))

    def _programar_solicitud_entrada_salida(self, proceso: Proceso):
        if proceso.quantum <= configuracion.TICK_MS or self._generador_aleatorio.random() * 100 >= proceso.interactividad:
            return None
        return self._generador_aleatorio.randrange(configuracion.TICK_MS, proceso.quantum, configuracion.TICK_MS)

    def _finalizar_proceso(self, proceso: Proceso):
        self.linea.cerrar()
        proceso.estado = Estado.TERMINADO
        self.terminados.agregar(proceso)
        self.en_cpu = None
        self._registrar_evento(f"{proceso.nombre} terminó.")

    def _suspender_por_entrada_salida(self, proceso: Proceso):
        self.linea.cerrar()
        proceso.estado = Estado.SUSPENDIDO
        proceso.causa_bloqueo = self._generador_aleatorio.choice(configuracion.CAUSAS_BLOQUEO)
        proceso.bloqueo_total = proceso.bloqueo_restante = self._sortear_duracion_en_milisegundos(*configuracion.BLOQUEO_DURACION_RANGO)
        proceso.bloqueo_en = None
        proceso.quantum_usado = 0
        self.suspendidos.agregar(proceso)
        self.en_cpu = None
        self._registrar_evento(f"{proceso.nombre} se suspende: {proceso.causa_bloqueo} ({proceso.bloqueo_total} ms).")

    def _devolver_por_quantum_agotado(self, proceso: Proceso):
        self.linea.cerrar()
        proceso.quantum_usado = 0
        self.en_cpu = None
        self._registrar_evento(f"{proceso.nombre} agotó su quantum.")
        self._agregar_a_preparados(proceso)

    def _registrar_evento(self, mensaje: str):
        self.eventos.append(f"[{self.reloj:>6} ms] {mensaje}")
