"""Regresiones del planificador, tiempos y controles. No requieren pantalla."""
import unittest
from simulacion.motor import MotorSimulacion
from simulacion.estados import Estado
from simulacion import planificador


class SimulationTests(unittest.TestCase):
    def setUp(self):
        self.motor = MotorSimulacion(seed=7)


    def crear_proceso(self, tiempo_total=100, prioridad=3, interactividad=0):
        return self.motor.agregar_proceso(prioridad=prioridad, tiempo_total=tiempo_total, interactividad=interactividad)

    def test_exact_completion_and_gantt(self):
        proceso = self.crear_proceso(15)
        self.motor.paso()
        self.motor.paso()
        self.assertEqual((proceso.tiempo_ejecutado, self.motor.reloj), (15, 15))
        self.assertEqual(sum(segmento.duracion for segmento in self.motor.linea.segmentos), 15)
        self.assertEqual(proceso.estado, Estado.TERMINADO)
        self.assertIsNone(self.motor.linea.abierto)

    def test_remainder_of_tick_is_used_by_next_process(self):
        primer_proceso, segundo_proceso = self.crear_proceso(3), self.crear_proceso(12)
        self.motor.paso()
        self.assertEqual((primer_proceso.tiempo_ejecutado, segundo_proceso.tiempo_ejecutado, segundo_proceso.tiempo_espera), (3, 7, 3))
        self.motor.paso()
        self.assertEqual((self.motor.reloj, segundo_proceso.tiempo_ejecutado), (15, 12))

    def test_scheduler_priority_quantum_and_fifo(self):
        proceso_inicial = self.crear_proceso(100, 1)
        primer_proceso = self.crear_proceso(100, 5)
        segundo_proceso = self.crear_proceso(200, 5)
        tercer_proceso = self.crear_proceso(200, 5)
        self.assertIs(planificador.seleccionar_siguiente_proceso(self.motor.preparados), segundo_proceso)
        for _ in range(2):
            self.motor.paso()
        self.assertIs(self.motor.en_cpu, segundo_proceso)
        self.assertEqual(planificador.ordenar_preparados([primer_proceso, segundo_proceso, tercer_proceso, proceso_inicial]), [segundo_proceso, tercer_proceso, primer_proceso, proceso_inicial])

    def test_rate_change_preserves_current_turn_and_io(self):
        proceso = self.crear_proceso(1000, interactividad=100)
        self.motor.paso()
        turno_anterior = proceso.quantum, proceso.bloqueo_en, proceso.quantum_usado
        proceso_en_cola = self.crear_proceso(500)
        self.motor.cambiar_divisor_quantum(10)
        self.assertEqual((proceso.quantum, proceso.bloqueo_en, proceso.quantum_usado), turno_anterior)
        self.assertEqual(proceso_en_cola.quantum, 50)
        for _ in range(2000):
            self.motor.paso()
            if self.motor.en_cpu is proceso and proceso.quantum == 100:
                break
        else:
            self.fail("El próximo turno no adoptó la nueva rata")

    def test_new_rate_is_used_before_requeue_ordering(self):
        proceso = self.crear_proceso(100)
        self.motor.preparar_ejecucion()
        proceso.quantum_usado = proceso.quantum - 10
        self.motor.cambiar_divisor_quantum(10)
        self.motor.paso()
        self.assertEqual(proceso.quantum, 10)

    def test_io_release_does_not_add_an_extra_tick_of_wait(self):
        proceso = self.crear_proceso(100)
        self.motor.preparar_ejecucion()
        proceso.bloqueo_en = 3
        self.motor._sortear_duracion_en_milisegundos = lambda *_: 7
        self.motor.paso()
        self.assertEqual(self.motor.reloj, 10)
        self.assertEqual(proceso.tiempo_ejecutado, 3)
        self.assertEqual(proceso.tiempo_espera, 0)
        self.assertIs(self.motor.en_cpu, proceso)
        self.assertEqual(proceso.bloqueo_restante, 0)

    def test_completion_and_reset_clear_state(self):
        self.crear_proceso(3)
        self.motor.paso()
        self.motor.reiniciar()
        self.assertEqual(self.motor.reloj, 0)
        self.assertFalse(self.motor.procesos)
        self.assertFalse(self.motor.linea.segmentos)
        self.assertIsNone(self.motor.en_cpu)

    def test_invalid_inputs_are_rejected_without_creating_a_process(self):
        for tiempo_total in [0, -1, 1.5, True]:
            with self.assertRaises(ValueError):
                self.crear_proceso(tiempo_total)
        for interactividad in [-1, 101]:
            with self.assertRaises(ValueError):
                self.crear_proceso(interactividad=interactividad)
        with self.assertRaises(ValueError):
            self.motor.cambiar_divisor_quantum(0)
        self.assertFalse(self.motor.procesos)
        self.assertEqual(self.crear_proceso().pid, 101)

    def test_many_seeded_runs_preserve_process_and_timeline_invariants(self):
        for seed in range(20):
            motor = MotorSimulacion(seed=seed)
            for numero_proceso in range(8):
                motor.agregar_proceso(prioridad=1 + numero_proceso % 5, tiempo_total=3 + numero_proceso * 37, interactividad=numero_proceso * 14)
            for numero_paso in range(3000):
                cambios_divisor = {5: 2, 15: 10, 40: 3}
                if numero_paso in cambios_divisor:
                    motor.cambiar_divisor_quantum(cambios_divisor[numero_paso])
                motor.paso()
                procesos_por_estado = [*motor.preparados, *motor.suspendidos, *motor.terminados]
                if motor.en_cpu is not None:
                    procesos_por_estado.append(motor.en_cpu)
                self.assertEqual(len({proceso.pid for proceso in procesos_por_estado}), 8)
                self.assertEqual(len(procesos_por_estado), 8)
                for proceso in motor.procesos.values():
                    self.assertLessEqual(proceso.tiempo_ejecutado, proceso.tiempo_total)
                    self.assertGreaterEqual(proceso.bloqueo_restante, 0)
                if len(motor.terminados) == 8:
                    break
            self.assertEqual(len(motor.terminados), 8)
            for proceso in motor.terminados:
                self.assertEqual(sum(segmento.duracion for segmento in motor.linea.segmentos if segmento.pid == proceso.pid), proceso.tiempo_total)
            for primer_proceso, segundo_proceso in zip(motor.linea.segmentos, motor.linea.segmentos[1:]):
                self.assertLessEqual(primer_proceso.fin, segundo_proceso.inicio)

