"""Integración entre el motor, las acciones y el reloj de reproducción."""
import os
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
import unittest
from PySide6.QtWidgets import QApplication
from aplicacion.controlador import ControladorSimulacion

APP = QApplication.instance() or QApplication([])


class ControladorTests(unittest.TestCase):
    def setUp(self):
        self.controlador = ControladorSimulacion(seed=7)

    def tearDown(self):
        self.controlador.pausar()

    def test_fin_detiene_reproduccion_y_reinicio_conserva_preferencias(self):
        c = self.controlador
        c.set_velocidad(50)
        c.set_rata(10)
        p = c.agregar_proceso(tiempo_total=3, interactividad=0)
        c.seleccionar(p.pid)
        c.iniciar()
        self.assertTrue(c.corriendo)
        c.paso()
        self.assertFalse(c.corriendo)
        self.assertEqual(c.motor.reloj, 3)
        c.reiniciar()
        self.assertIsNone(c.seleccion)
        self.assertEqual(c.motor.rata, 10)
        self.assertEqual(c.temporizador.interval(), 50)
        self.assertFalse(c.motor.hay_trabajo)

    def test_eventos_se_publican_una_sola_vez_con_estado_consistente(self):
        c = self.controlador
        eventos = []
        c.evento.connect(eventos.append)
        c.agregar_proceso(tiempo_total=3, interactividad=0)
        c.paso()
        anteriores = list(eventos)
        c.paso()
        self.assertEqual(eventos, anteriores)
        self.assertTrue(any("terminó" in e for e in eventos))
        self.assertEqual(c.motor.extraer_eventos(), [])

    def test_no_inicia_sin_trabajo(self):
        self.controlador.iniciar()
        self.assertFalse(self.controlador.corriendo)
