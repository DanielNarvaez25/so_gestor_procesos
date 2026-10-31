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
