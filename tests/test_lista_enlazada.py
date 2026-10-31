"""Enlaces, eliminación durante el recorrido e integración con el motor."""
import unittest

from estructuras import ListaEnlazada
from simulacion.motor import MotorSimulacion


class ListaEnlazadaTests(unittest.TestCase):
    def test_lista_vacia_y_orden_de_insercion(self):
        lista = ListaEnlazada()
        self.assertFalse(lista)
        self.assertEqual(list(lista), [])
        for nombre in ("Ana", "Luis", "Carlos"):
            lista.agregar(nombre)
        self.assertEqual(len(lista), 3)
        self.assertEqual(list(lista), ["Ana", "Luis", "Carlos"])
        self.assertEqual(list(lista), list(lista))

    def test_eliminar_inicio_medio_final_y_unico(self):
        lista = ListaEnlazada(("Ana", "Luis", "Carlos", "Marta"))
        lista.eliminar("Ana")
        lista.eliminar("Carlos")
        self.assertEqual(list(lista), ["Luis", "Marta"])
        lista.eliminar("Marta")
        lista.agregar("Pedro")
        self.assertEqual(list(lista), ["Luis", "Pedro"])
        lista.eliminar("Luis")
        lista.eliminar("Pedro")
        self.assertFalse(lista)
        lista.agregar("Nuevo")
        self.assertEqual(list(lista), ["Nuevo"])
        self.assertEqual(len(lista), 1)

    def test_duplicados_dato_ausente_y_limpieza(self):
        lista = ListaEnlazada((1, 2, 1))
        lista.eliminar(1)
        self.assertEqual(list(lista), [2, 1])
        with self.assertRaises(ValueError):
            lista.eliminar(99)
        self.assertEqual(len(lista), 2)
        lista.limpiar()
        self.assertFalse(lista)
        with self.assertRaises(ValueError):
            lista.eliminar(1)
        lista.agregar(3)
        self.assertEqual(list(lista), [3])

    def test_eliminar_actual_no_salta_nodos_durante_recorrido(self):
        lista = ListaEnlazada(range(6))
        visitados = []
        for numero in lista:
            visitados.append(numero)
            lista.eliminar(numero)
        self.assertEqual(visitados, list(range(6)))
        self.assertFalse(lista)
        lista.agregar(10)
        self.assertEqual(list(lista), [10])

    def test_motor_libera_varios_suspendidos_en_el_mismo_instante(self):
        motor = MotorSimulacion(seed=7)
        primero = motor.agregar_proceso(tiempo_total=100, interactividad=0)
        segundo = motor.agregar_proceso(tiempo_total=100, interactividad=0)
        motor.preparados.eliminar(segundo)
        for proceso in (primero, segundo):
            motor.en_cpu = proceso
            motor._suspender_por_entrada_salida(proceso)
            proceso.bloqueo_restante = 10
        motor.paso()
        self.assertFalse(motor.suspendidos)
        self.assertIs(motor.en_cpu, primero)
        self.assertEqual(list(motor.preparados), [segundo])
        self.assertIs(motor.buscar(segundo.pid), segundo)
        motor.reiniciar()
        for coleccion in (motor.preparados, motor.suspendidos, motor.terminados):
            self.assertIsInstance(coleccion, ListaEnlazada)
            self.assertFalse(coleccion)


if __name__ == "__main__":
    unittest.main()
