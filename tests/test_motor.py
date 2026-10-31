"""Regresiones del planificador, tiempos y controles. No requieren pantalla."""
import unittest
from simulacion.motor import MotorSimulacion
from simulacion.estados import Estado
from simulacion import planificador as scheduler


class SimulationTests(unittest.TestCase):
    def setUp(self):
        self.sim = MotorSimulacion(seed=7)


    def add(self, total=100, priority=3, io=0):
        return self.sim.agregar_proceso(prioridad=priority, tiempo_total=total, interactividad=io)

    def test_exact_completion_and_gantt(self):
        p = self.add(15)
        self.sim.paso()
        self.sim.paso()
        self.assertEqual((p.tiempo_ejecutado, self.sim.reloj), (15, 15))
        self.assertEqual(sum(s.duracion for s in self.sim.linea.segmentos), 15)
        self.assertEqual(p.estado, Estado.TERMINADO)
        self.assertIsNone(self.sim.linea.abierto)

    def test_remainder_of_tick_is_used_by_next_process(self):
        a, b = self.add(3), self.add(12)
        self.sim.paso()
        self.assertEqual((a.tiempo_ejecutado, b.tiempo_ejecutado, b.tiempo_espera), (3, 7, 3))
        self.sim.paso()
        self.assertEqual((self.sim.reloj, b.tiempo_ejecutado), (15, 12))

    def test_scheduler_priority_quantum_and_fifo(self):
        first = self.add(100, 1)
        a = self.add(100, 5)
        b = self.add(200, 5)
        c = self.add(200, 5)
        self.assertIs(scheduler.elegir(self.sim.preparados), b)
        for _ in range(2): self.sim.paso()
        self.assertIs(self.sim.en_cpu, b)
        self.assertEqual(sorted([a, b, c, first], key=scheduler.clave_orden), [b, c, a, first])

    def test_rate_change_preserves_current_turn_and_io(self):
        p = self.add(1000, io=100)
        self.sim.paso()
        previous = p.quantum, p.bloqueo_en, p.quantum_usado
        queued = self.add(500)
        self.sim.set_rata(10)
        self.assertEqual((p.quantum, p.bloqueo_en, p.quantum_usado), previous)
        self.assertEqual(queued.quantum, 50)
        for _ in range(2000):
            self.sim.paso()
            if self.sim.en_cpu is p and p.quantum == 100:
                break
        else:
            self.fail("El próximo turno no adoptó la nueva rata")

    def test_new_rate_is_used_before_requeue_ordering(self):
        p = self.add(100)
        p.quantum_usado = p.quantum - 10
        self.sim.set_rata(10)
        self.sim.paso()
        self.assertEqual(p.quantum, 10)

    def test_io_release_does_not_add_an_extra_tick_of_wait(self):
        p = self.add(100)
        p.bloqueo_en = 3
        self.sim._multiplo = lambda *_: 7
        self.sim.paso()
        self.assertEqual(self.sim.reloj, 10)
        self.assertEqual(p.tiempo_ejecutado, 3)
        self.assertEqual(p.tiempo_espera, 0)
        self.assertIs(self.sim.en_cpu, p)
        self.assertEqual(p.bloqueo_restante, 0)

    def test_completion_and_reset_clear_state(self):
        self.add(3)
        self.sim.paso()
        self.sim.reiniciar()
        self.assertEqual(self.sim.reloj, 0)
        self.assertFalse(self.sim.procesos)
        self.assertFalse(self.sim.linea.segmentos)
        self.assertIsNone(self.sim.en_cpu)

    def test_invalid_inputs_are_rejected_without_creating_a_process(self):
        for total in [0, -1, 1.5, True]:
            with self.assertRaises(ValueError): self.add(total)
        for io in [-1, 101]:
            with self.assertRaises(ValueError): self.add(io=io)
        with self.assertRaises(ValueError): self.sim.set_rata(0)
        self.assertFalse(self.sim.procesos)
        self.assertEqual(self.add().pid, 101)

    def test_many_seeded_runs_preserve_process_and_timeline_invariants(self):
        for seed in range(20):
            sim = MotorSimulacion(seed=seed)
            for n in range(8):
                sim.agregar_proceso(prioridad=1 + n % 5, tiempo_total=3 + n * 37, interactividad=n * 14)
            for step in range(3000):
                if step in (5, 15, 40): sim.set_rata([2, 10, 3][(5, 15, 40).index(step)])
                sim.paso()
                states = sim.preparados + sim.suspendidos + sim.terminados + ([sim.en_cpu] if sim.en_cpu else [])
                self.assertEqual(len({p.pid for p in states}), 8)
                self.assertEqual(len(states), 8)
                for p in sim.procesos.values():
                    self.assertLessEqual(p.tiempo_ejecutado, p.tiempo_total)
                    self.assertGreaterEqual(p.bloqueo_restante, 0)
                if len(sim.terminados) == 8: break
            self.assertEqual(len(sim.terminados), 8)
            for p in sim.terminados:
                self.assertEqual(sum(s.duracion for s in sim.linea.segmentos if s.pid == p.pid), p.tiempo_total)
            for a, b in zip(sim.linea.segmentos, sim.linea.segmentos[1:]):
                self.assertLessEqual(a.fin, b.inicio)

