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
        self.eventos = []
        self._limpiar()

    def _limpiar(self):
        self.reloj = 0
        self._siguiente_pid = configuracion.PID_INICIAL
        self._contador_cola = 0
        self.procesos = {}
        self.preparados = ListaEnlazada()
        self.suspendidos = ListaEnlazada()
        self.terminados = ListaEnlazada()
        self.en_cpu = None

    @property
    def hay_trabajo(self):
        if self.en_cpu is not None:
            return True
        if len(self.preparados) > 0:
            return True
        if len(self.suspendidos) > 0:
            return True
        return False

    def preparados_ordenados(self):
        procesos_para_mostrar = planificador.ordenar_preparados(self.preparados)
        return procesos_para_mostrar

    def buscar(self, pid):
        return self.procesos.get(pid)

    def reiniciar(self):
        self._limpiar()
        self.linea.limpiar()
        self.eventos.clear()
        self._registrar_evento("Simulación reiniciada.")

    def extraer_eventos(self):
        eventos = self.eventos
        self.eventos = []
        return eventos

    def agregar_aleatorio(self, nombre=""):
        from .generador import datos_aleatorios
        datos_del_proceso = datos_aleatorios(self._generador_aleatorio)
        return self.agregar_proceso(nombre, **datos_del_proceso)

    def cambiar_divisor_quantum(self, divisor_quantum):
        """Cambia el divisor del quantum para los próximos turnos de CPU."""
        if divisor_quantum not in configuracion.DIVISORES_QUANTUM:
            raise ValueError("Rata de quantum no admitida")
        self.divisor_quantum = divisor_quantum
        for proceso in self.procesos.values():
            if proceso.estado == Estado.TERMINADO:
                continue
            if proceso.estado == Estado.EJECUCION:
                continue
            nuevo_quantum = planificador.calcular_quantum(proceso.tiempo_total, divisor_quantum)
            proceso.quantum = nuevo_quantum
        self._registrar_evento(f"Rata de quantum = {divisor_quantum}. Se aplicará desde el próximo turno de CPU.")


    def agregar_proceso(self, nombre="", prioridad=3, tiempo_total=None, interactividad=None):
        if tiempo_total is not None:
            if not isinstance(tiempo_total, int):
                raise ValueError("El tiempo total debe ser un entero positivo")
            if isinstance(tiempo_total, bool):
                raise ValueError("El tiempo total debe ser un entero positivo")
            if tiempo_total <= 0:
                raise ValueError("El tiempo total debe ser un entero positivo")
        if interactividad is not None:
            interactividad_es_entera = isinstance(interactividad, int)
            if not interactividad_es_entera:
                raise ValueError("La interactividad debe estar entre 0 y 100")
            if interactividad < 0:
                raise ValueError("La interactividad debe estar entre 0 y 100")
            if interactividad > 100:
                raise ValueError("La interactividad debe estar entre 0 y 100")
        pid = self._siguiente_pid
        self._siguiente_pid += 1
        indice = pid - configuracion.PID_INICIAL
        nombre = nombre.strip()
        if nombre == "":
            letra_proceso = self._letra_del_proceso(indice)
            nombre = f"Proceso {letra_proceso}"
        prioridad = int(prioridad)
        if prioridad < configuracion.PRIORIDAD_MIN:
            prioridad = configuracion.PRIORIDAD_MIN
        if prioridad > configuracion.PRIORIDAD_MAX:
            prioridad = configuracion.PRIORIDAD_MAX
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
        return proceso

    @staticmethod
    def _letra_del_proceso(indice):
        letra = chr(ord("A") + indice % 26)
        if indice >= 26:
            numero_vuelta_alfabeto = indice // 26
            letra = letra + str(numero_vuelta_alfabeto)
        return letra

    def _sortear_duracion_en_milisegundos(self, minimo, maximo):
        return self._generador_aleatorio.randrange(minimo, maximo + 1, configuracion.TICK_MS)

    def preparar_ejecucion(self):
        """Elige un preparado si la CPU está libre, sin avanzar el reloj.

        Se utiliza al iniciar o dar un paso. Un turno ya asignado se conserva,
        incluso al reanudar después de una pausa.
        """
        if self.en_cpu is None:
            self._asignar_cpu_al_siguiente_proceso()

    def paso(self):
        """Avanza hasta 10 ms, atendiendo cada cambio en su instante exacto.
        """
        self.preparar_ejecucion()
        fin_del_paso = self.reloj + configuracion.TICK_MS

        while self.reloj < fin_del_paso:
            if not self.hay_trabajo:
                break
            tiempo_a_avanzar = self._tiempo_hasta_proximo_evento(fin_del_paso)
            self._avanzar_reloj_y_tiempos(tiempo_a_avanzar)
            self._reincorporar_procesos_con_entrada_salida_finalizada()
            self._resolver_estado_del_proceso_en_cpu()
            if self.en_cpu is None:
                self._asignar_cpu_al_siguiente_proceso()

    def _tiempo_hasta_proximo_evento(self, fin_del_paso):
        """Avanza solo hasta el primer evento: fin, quantum, E/S o fin del paso."""
        tiempo_disponible = fin_del_paso - self.reloj
        proceso_actual = self.en_cpu
        if proceso_actual is not None:
            quantum_restante = proceso_actual.quantum - proceso_actual.quantum_usado
            if proceso_actual.tiempo_restante < tiempo_disponible:
                tiempo_disponible = proceso_actual.tiempo_restante
            if quantum_restante < tiempo_disponible:
                tiempo_disponible = quantum_restante
            if proceso_actual.bloqueo_en is not None:
                tiempo_hasta_entrada_salida = (
                    proceso_actual.bloqueo_en - proceso_actual.quantum_usado
                )
                if tiempo_hasta_entrada_salida < tiempo_disponible:
                    tiempo_disponible = tiempo_hasta_entrada_salida
        for proceso_suspendido in self.suspendidos:
            tiempo_hasta_desbloqueo = proceso_suspendido.bloqueo_restante
            if tiempo_hasta_desbloqueo < tiempo_disponible:
                tiempo_disponible = tiempo_hasta_desbloqueo
        return tiempo_disponible

    def _avanzar_reloj_y_tiempos(self, tiempo_transcurrido):
        """Actualiza espera, E/S y ejecución durante el mismo intervalo."""
        for proceso_preparado in self.preparados:
            espera_acumulada = proceso_preparado.tiempo_espera + tiempo_transcurrido
            proceso_preparado.tiempo_espera = espera_acumulada
        for proceso_suspendido in self.suspendidos:
            espera_pendiente = proceso_suspendido.bloqueo_restante - tiempo_transcurrido
            proceso_suspendido.bloqueo_restante = espera_pendiente
        self.reloj += tiempo_transcurrido
        if self.en_cpu is not None:
            self.en_cpu.tiempo_ejecutado += tiempo_transcurrido
            self.en_cpu.quantum_usado += tiempo_transcurrido
            self.linea.extender(self.reloj)

    def _reincorporar_procesos_con_entrada_salida_finalizada(self):
        """Devuelve a preparados todos los que terminaron su espera de E/S."""
        for proceso_suspendido in self.suspendidos:
            if proceso_suspendido.bloqueo_restante == 0:
                self.suspendidos.eliminar(proceso_suspendido)
                self._registrar_evento(f"{proceso_suspendido.nombre} termina su E/S.")
                self._agregar_a_preparados(proceso_suspendido)

    def _resolver_estado_del_proceso_en_cpu(self):
        """Comprueba las salidas de CPU en este orden: fin, E/S y quantum."""
        proceso_actual = self.en_cpu
        if proceso_actual is None:
            return
        if proceso_actual.tiempo_restante == 0:
            self._finalizar_proceso(proceso_actual)
            return

        if proceso_actual.bloqueo_en is not None:
            llego_momento_entrada_salida = (
                proceso_actual.quantum_usado >= proceso_actual.bloqueo_en
            )
            if llego_momento_entrada_salida:
                self._suspender_por_entrada_salida(proceso_actual)
                return

        quantum_agotado = proceso_actual.quantum_usado >= proceso_actual.quantum
        if quantum_agotado:
            self._devolver_por_quantum_agotado(proceso_actual)

    def _agregar_a_preparados(self, proceso):
        proceso.estado = Estado.PREPARADO
        proceso.quantum = planificador.calcular_quantum(proceso.tiempo_total, self.divisor_quantum)
        self._contador_cola += 1
        proceso.orden_cola = self._contador_cola
        self.preparados.agregar(proceso)

    def _asignar_cpu_al_siguiente_proceso(self):
        proceso = planificador.seleccionar_siguiente_proceso(self.preparados)
        if proceso is None:
            return
        self.preparados.eliminar(proceso)
        proceso.estado = Estado.EJECUCION
        proceso.quantum = planificador.calcular_quantum(proceso.tiempo_total, self.divisor_quantum)
        proceso.quantum_usado = 0
        proceso.bloqueo_en = self._programar_solicitud_entrada_salida(proceso)
        self.en_cpu = proceso
        self.linea.abrir(proceso, self.reloj)
        self._registrar_evento(f"{proceso.nombre} entra a CPU.")

    def _programar_solicitud_entrada_salida(self, proceso):
        if proceso.quantum <= configuracion.TICK_MS:
            return None

        porcentaje_sorteado = self._generador_aleatorio.random() * 100
        if porcentaje_sorteado >= proceso.interactividad:
            return None

        momento_solicitud = self._generador_aleatorio.randrange(
            configuracion.TICK_MS, proceso.quantum, configuracion.TICK_MS
        )
        return momento_solicitud

    def _finalizar_proceso(self, proceso):
        self.linea.cerrar()
        proceso.estado = Estado.TERMINADO
        self.terminados.agregar(proceso)
        self.en_cpu = None
        self._registrar_evento(f"{proceso.nombre} terminó.")

    def _suspender_por_entrada_salida(self, proceso):
        self.linea.cerrar()
        proceso.estado = Estado.SUSPENDIDO
        proceso.causa_bloqueo = self._generador_aleatorio.choice(configuracion.CAUSAS_BLOQUEO)
        duracion_bloqueo = self._sortear_duracion_en_milisegundos(
            *configuracion.BLOQUEO_DURACION_RANGO
        )
        proceso.bloqueo_total = duracion_bloqueo
        proceso.bloqueo_restante = duracion_bloqueo
        proceso.bloqueo_en = None
        proceso.quantum_usado = 0
        self.suspendidos.agregar(proceso)
        self.en_cpu = None
        self._registrar_evento(f"{proceso.nombre} se suspende: {proceso.causa_bloqueo} ({proceso.bloqueo_total} ms).")

    def _devolver_por_quantum_agotado(self, proceso):
        self.linea.cerrar()
        proceso.quantum_usado = 0
        self.en_cpu = None
        self._registrar_evento(f"{proceso.nombre} agotó su quantum.")
        self._agregar_a_preparados(proceso)

    def _registrar_evento(self, mensaje):
        self.eventos.append(f"[{self.reloj:>6} ms] {mensaje}")
