"""Navegación del historial completo sin perder la posición de lectura."""
import os
os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
import unittest
from PySide6.QtWidgets import QApplication
from interfaz.componentes.grafico_gantt import HistorialCpu
from simulacion.motor import MotorSimulacion

APLICACION = QApplication.instance() or QApplication([])


class HistorialTests(unittest.TestCase):
    def test_historial_zoom_seguimiento_y_reinicio(self):
        motor = MotorSimulacion(seed=1)
        motor.agregar_proceso(tiempo_total=20000, interactividad=0)
        vista = HistorialCpu(motor.linea, motor.buscar)
        vista.resize(800, 300)
        vista.show()
        try:
            for _ in range(900):
                motor.paso()
            vista.refrescar(motor.reloj)
            APLICACION.processEvents()
            barra = vista.scroll.horizontalScrollBar()
            self.assertGreater(barra.maximum(), 0)
            self.assertEqual(barra.value(), barra.maximum())
            barra.setValue(0)
            self.assertFalse(vista.seguir.isChecked())
            primero = vista._lienzo._segmentos[0]
            self.assertEqual(primero.inicio, 0)
            self.assertIs(vista._lienzo._segmento_en(vista._lienzo._rectangulo_segmento(primero).center()), primero)
            motor.paso()
            vista.refrescar(motor.reloj)
            APLICACION.processEvents()
            self.assertEqual(barra.value(), 0)
            ancho = vista._lienzo.minimumWidth()
            vista.zoom.setCurrentIndex(2)
            APLICACION.processEvents()
            self.assertGreater(vista._lienzo.minimumWidth(), ancho)
            vista.ir_actual()
            self.assertTrue(vista.seguir.isChecked())
            self.assertEqual(barra.value(), barra.maximum())
            motor.reiniciar()
            vista.refrescar(0)
            APLICACION.processEvents()
            self.assertEqual(barra.value(), 0)
            self.assertEqual(barra.maximum(), 0)
            self.assertFalse(vista._lienzo._segmentos)
        finally:
            vista.close()
