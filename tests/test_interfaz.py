import os
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
import unittest
from PySide6.QtWidgets import QApplication
APP = QApplication.instance() or QApplication([])

class InterfaceTests(unittest.TestCase):
    def test_gantt_can_paint_during_dispatch_and_reset(self):
        import sys
        from interfaz.ventana_principal import VentanaPrincipal
        w = VentanaPrincipal()
        errors = []
        old_hook = sys.excepthook
        sys.excepthook = lambda *args: errors.append(args)
        try:
            w.show()
            APP.processEvents()
            w.controlador.segmento.connect(lambda _: w.gantt._lienzo.repaint())
            for _ in range(4):
                w.controlador.agregar_proceso(tiempo_total=13, interactividad=0)
            for _ in range(6):
                w.controlador.paso()
                APP.processEvents()
            w.controlador.reiniciar()
            APP.processEvents()
            w.gantt._lienzo.repaint()
            self.assertFalse(w.gantt._lienzo._segmentos)
            self.assertFalse(errors)
        finally:
            sys.excepthook = old_hook
            w.controlador.pausar()
            w.close()

    def test_controls_selection_and_reset(self):
        from interfaz.ventana_principal import VentanaPrincipal
        from interfaz.estilos.tema import aplicar_tema
        aplicar_tema(APP)
        w = VentanaPrincipal()
        try:
            self.assertFalse(w.toolbar._play.isEnabled())
            w.form._tiempo.setValue(15)
            w.form._interactividad.setValue(0)
            w.form.agregar.click()
            self.assertEqual(w.controlador.motor.en_cpu.tiempo_total, 15)
            self.assertEqual(w.controlador.seleccion, 101)
            w.toolbar._paso.click()
            self.assertEqual(w.controlador.motor.reloj, 10)
            w.toolbar._play.click()
            self.assertTrue(w.controlador.corriendo)
            w.toolbar._pausa.click()
            self.assertFalse(w.controlador.corriendo)
            w.toolbar._rata.setCurrentIndex(w.toolbar._rata.findData(10))
            w.toolbar._paso.click()
            self.assertEqual(w.controlador.motor.reloj, 15)
            self.assertEqual(w.estado.text(), "✓  Completado")
            self.assertFalse(w.toolbar._play.isEnabled())
            w.terminados.seleccionado.emit(101)
            self.assertEqual(w.controlador.seleccion, 101)
            self.assertIn("terminó", w.statusBar().currentMessage())
            w.controlador.reiniciar()
            self.assertIsNone(w.controlador.seleccion)
            self.assertEqual(w.summary.valores[0].text(), "0 ms")
            self.assertNotIn("terminó", w.statusBar().currentMessage())
        finally:
            w.controlador.pausar()
            w.close()

if __name__ == "__main__":
    unittest.main()
