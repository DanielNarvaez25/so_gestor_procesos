import os
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
import unittest
from PySide6.QtWidgets import QApplication
APLICACION = QApplication.instance() or QApplication([])

class InterfaceTests(unittest.TestCase):
    def test_gantt_can_paint_during_dispatch_and_reset(self):
        import sys
        from interfaz.ventana_principal import VentanaPrincipal
        ventana = VentanaPrincipal()
        errores = []
        manejador_anterior = sys.excepthook
        sys.excepthook = lambda *argumentos: errores.append(argumentos)
        try:
            ventana.show()
            APLICACION.processEvents()
            ventana.controlador.segmento.connect(lambda _: ventana.historial_cpu._lienzo.repaint())
            for _ in range(4):
                ventana.controlador.agregar_proceso(tiempo_total=13, interactividad=0)
            for _ in range(6):
                ventana.controlador.paso()
                APLICACION.processEvents()
            ventana.controlador.reiniciar()
            APLICACION.processEvents()
            ventana.historial_cpu._lienzo.repaint()
            self.assertFalse(ventana.historial_cpu._lienzo._segmentos)
            self.assertFalse(errores)
        finally:
            sys.excepthook = manejador_anterior
            ventana.controlador.pausar()
            ventana.close()

    def test_controls_selection_and_reset(self):
        from interfaz.ventana_principal import VentanaPrincipal
        from interfaz.estilos.tema import aplicar_tema
        aplicar_tema(APLICACION)
        ventana = VentanaPrincipal()
        try:
            self.assertFalse(ventana.barra_controles._boton_iniciar.isEnabled())
            ventana.formulario._tiempo.setValue(15)
            ventana.formulario._interactividad.setValue(0)
            ventana.formulario.agregar.click()
            self.assertEqual(ventana.controlador.motor.en_cpu.tiempo_total, 15)
            self.assertEqual(ventana.controlador.seleccion, 101)
            ventana.barra_controles._boton_paso.click()
            self.assertEqual(ventana.controlador.motor.reloj, 10)
            ventana.barra_controles._boton_iniciar.click()
            self.assertTrue(ventana.controlador.corriendo)
            ventana.barra_controles._boton_pausar.click()
            self.assertFalse(ventana.controlador.corriendo)
            ventana.barra_controles._selector_divisor_quantum.setCurrentIndex(ventana.barra_controles._selector_divisor_quantum.findData(10))
            ventana.barra_controles._boton_paso.click()
            self.assertEqual(ventana.controlador.motor.reloj, 15)
            self.assertEqual(ventana.estado.text(), "✓  Completado")
            self.assertFalse(ventana.barra_controles._boton_iniciar.isEnabled())
            ventana.terminados.seleccionado.emit(101)
            self.assertEqual(ventana.controlador.seleccion, 101)
            self.assertIn("terminó", ventana.statusBar().currentMessage())
            ventana.controlador.reiniciar()
            self.assertIsNone(ventana.controlador.seleccion)
            self.assertEqual(ventana.resumen.valores[0].text(), "0 ms")
            self.assertNotIn("terminó", ventana.statusBar().currentMessage())
        finally:
            ventana.controlador.pausar()
            ventana.close()

if __name__ == "__main__":
    unittest.main()
