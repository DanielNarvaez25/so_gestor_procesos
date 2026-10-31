"""Integración entre el motor, las acciones y el reloj de reproducción."""
import os
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
import unittest
from PySide6.QtWidgets import QApplication
from aplicacion.controlador import ControladorSimulacion

APLICACION = QApplication.instance() or QApplication([])


class ControladorTests(unittest.TestCase):
    def setUp(self):
        self.controlador = ControladorSimulacion(seed=7)

    def tearDown(self):
        self.controlador.pausar()

    def test_fin_detiene_reproduccion_y_reinicio_conserva_preferencias(self):
        controlador = self.controlador
        controlador.set_velocidad(50)
        controlador.cambiar_divisor_quantum(10)
        proceso = controlador.agregar_proceso(tiempo_total=3, interactividad=0)
        controlador.seleccionar(proceso.pid)
        controlador.iniciar()
        self.assertTrue(controlador.corriendo)
        controlador.paso()
        self.assertFalse(controlador.corriendo)
        self.assertEqual(controlador.motor.reloj, 3)
        controlador.reiniciar()
        self.assertIsNone(controlador.seleccion)
        self.assertEqual(controlador.motor.divisor_quantum, 10)
        self.assertEqual(controlador.temporizador.interval(), 50)
        self.assertFalse(controlador.motor.hay_trabajo)

    def test_eventos_se_publican_una_sola_vez_con_estado_consistente(self):
        controlador = self.controlador
        eventos = []
        controlador.evento.connect(eventos.append)
        controlador.agregar_proceso(tiempo_total=3, interactividad=0)
        controlador.paso()
        anteriores = list(eventos)
        controlador.paso()
        self.assertEqual(eventos, anteriores)
        self.assertTrue(any("terminó" in mensaje for mensaje in eventos))
        self.assertEqual(controlador.motor.extraer_eventos(), [])

    def test_no_inicia_sin_trabajo(self):
        self.controlador.iniciar()
        self.assertFalse(self.controlador.corriendo)

    def test_iniciar_y_paso_seleccionan_entre_todos_los_preparados(self):
        for accion in ("iniciar", "paso"):
            with self.subTest(accion=accion):
                controlador = self.controlador
                controlador.reiniciar()
                baja = controlador.agregar_proceso(prioridad=1, tiempo_total=100, interactividad=0)
                corto = controlador.agregar_proceso(prioridad=5, tiempo_total=100, interactividad=0)
                elegido = controlador.agregar_proceso(prioridad=5, tiempo_total=200, interactividad=0)
                reciente = controlador.agregar_proceso(prioridad=5, tiempo_total=200, interactividad=0)
                self.assertIsNone(controlador.motor.en_cpu)
                self.assertEqual(list(controlador.motor.preparados), [baja, corto, elegido, reciente])
                self.assertEqual(controlador.motor.reloj, 0)
                self.assertFalse(controlador.motor.linea.segmentos)

                getattr(controlador, accion)()

                self.assertIs(controlador.motor.en_cpu, elegido)
                self.assertEqual(len(controlador.motor.preparados), 3)
                tiempo_esperado = 0 if accion == "iniciar" else 10
                self.assertEqual(controlador.motor.reloj, tiempo_esperado)
                self.assertEqual(elegido.tiempo_ejecutado, tiempo_esperado)
                self.assertEqual(controlador.motor.extraer_eventos(), [])
                controlador.pausar()

    def test_agregar_y_reanudar_no_interrumpen_el_turno_actual(self):
        controlador = self.controlador
        actual = controlador.agregar_proceso(prioridad=1, tiempo_total=100, interactividad=0)
        controlador.iniciar()
        controlador.paso()
        controlador.pausar()
        quantum_usado = actual.quantum_usado
        bloqueo_programado = actual.bloqueo_en
        prioritario = controlador.agregar_proceso(prioridad=5, tiempo_total=1000, interactividad=0)
        self.assertIs(controlador.motor.en_cpu, actual)
        self.assertEqual(list(controlador.motor.preparados), [prioritario])

        controlador.iniciar()

        self.assertIs(controlador.motor.en_cpu, actual)
        self.assertEqual(actual.quantum_usado, quantum_usado)
        self.assertEqual(actual.bloqueo_en, bloqueo_programado)
        self.assertEqual(controlador.motor.reloj, 10)
        controlador.paso()
        self.assertEqual(controlador.motor.reloj, 20)
        self.assertIs(controlador.motor.en_cpu, prioritario)
        self.assertEqual(actual.tiempo_ejecutado, 20)
        self.assertEqual(prioritario.tiempo_ejecutado, 0)
