"""Reglas PMA-QMG-P y orden visible de los procesos preparados."""
import unittest
from itertools import permutations

from estructuras import ListaEnlazada
from simulacion import planificador
from simulacion.proceso import Proceso


class PlanificadorTests(unittest.TestCase):
    def test_prioridad_quantum_y_llegada_en_cualquier_orden_de_recorrido(self):
        prioridad_baja = Proceso(101, "Prioridad baja", 1, 1000, 500, orden_cola=1)
        quantum_menor = Proceso(102, "Quantum menor", 5, 1000, 100, orden_cola=2)
        llegada_antigua = Proceso(103, "Llegada antigua", 5, 1000, 200, orden_cola=3)
        llegada_reciente = Proceso(104, "Llegada reciente", 5, 1000, 200, orden_cola=4)
        orden_esperado = [llegada_antigua, llegada_reciente, quantum_menor, prioridad_baja]

        for orden_entrada in permutations(orden_esperado):
            preparados = ListaEnlazada(orden_entrada)
            self.assertIs(
                planificador.seleccionar_siguiente_proceso(preparados), llegada_antigua
            )
            self.assertEqual(planificador.ordenar_preparados(preparados), orden_esperado)
            self.assertEqual(list(preparados), list(orden_entrada))
            for proceso in preparados:
                self.assertEqual(proceso.quantum_usado, 0)

    def test_empate_completo_conserva_el_orden_original(self):
        primero = Proceso(101, "Primero", 3, 1000, 200, orden_cola=1)
        segundo = Proceso(102, "Segundo", 3, 1000, 200, orden_cola=1)
        for orden_entrada in ((primero, segundo), (segundo, primero)):
            preparados = ListaEnlazada(orden_entrada)
            self.assertIs(
                planificador.seleccionar_siguiente_proceso(preparados), orden_entrada[0]
            )
            self.assertEqual(planificador.ordenar_preparados(preparados), list(orden_entrada))

    def test_sin_preparados_no_hay_proceso_elegido(self):
        preparados = ListaEnlazada()
        self.assertIsNone(planificador.seleccionar_siguiente_proceso(preparados))
        self.assertEqual(planificador.ordenar_preparados(preparados), [])


if __name__ == "__main__":
    unittest.main()
