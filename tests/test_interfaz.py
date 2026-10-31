import os
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
import unittest
from PySide6.QtWidgets import QApplication
APLICACION = QApplication.instance() or QApplication([])

class InterfaceTests(unittest.TestCase):
    def test_vista_previa_sigue_la_preferencia_sin_asignar_ni_interrumpir_cpu(self):
        from interfaz.ventana_principal import VentanaPrincipal
        from simulacion.estados import Estado

        ventana = VentanaPrincipal()
        controlador = ventana.controlador
        motor = controlador.motor
        try:
            self.assertEqual(ventana.cpu._nombre.toolTip(), "CPU libre")
            baja = controlador.agregar_proceso(nombre="Baja", prioridad=1, tiempo_total=1000, interactividad=0)
            self.assertEqual(ventana.cpu._nombre.toolTip(), baja.nombre)
            alta = controlador.agregar_proceso(nombre="Alta", prioridad=5, tiempo_total=100, interactividad=0)
            self.assertEqual(ventana.cpu._nombre.toolTip(), alta.nombre)
            mayor_quantum = controlador.agregar_proceso(nombre="Mayor quantum", prioridad=5, tiempo_total=200, interactividad=0)
            reciente = controlador.agregar_proceso(nombre="Más reciente", prioridad=5, tiempo_total=200, interactividad=0)
            self.assertEqual(ventana.cpu._nombre.toolTip(), mayor_quantum.nombre)
            self.assertEqual(ventana.cpu._titulo.text(), "CPU / PRÓXIMO PROCESO")
            self.assertEqual(ventana.bcp_ejecucion._titulo.text(), "BCP · PRÓXIMO PROCESO")
            self.assertEqual(ventana.bcp_ejecucion._valores[0].text(), str(mayor_quantum.pid))
            self.assertIsNone(motor.en_cpu)
            self.assertEqual(len(motor.preparados), 4)
            for proceso in (baja, alta, mayor_quantum, reciente):
                self.assertEqual(proceso.estado, Estado.PREPARADO)
                self.assertEqual(proceso.tiempo_ejecutado, 0)
            self.assertEqual(motor.reloj, 0)
            self.assertFalse(motor.linea.segmentos)
            self.assertEqual(ventana.cpu._barra_quantum.value(), 0)

            controlador.iniciar()
            controlador.paso()
            controlador.pausar()
            turno_usado = mayor_quantum.quantum_usado
            controlador.agregar_proceso(nombre="Quantum superior", prioridad=5, tiempo_total=1000, interactividad=0)
            self.assertIs(motor.en_cpu, mayor_quantum)
            self.assertEqual(ventana.cpu._nombre.toolTip(), mayor_quantum.nombre)
            self.assertEqual(ventana.cpu._titulo.text(), "CPU / EJECUCIÓN ACTUAL")
            self.assertEqual(ventana.bcp_ejecucion._titulo.text(), "BCP · EN CPU")
            self.assertEqual(mayor_quantum.quantum_usado, turno_usado)
            self.assertEqual(ventana.cpu._barra_quantum.value(), mayor_quantum.progreso_quantum)

            controlador.reiniciar()
            self.assertEqual(ventana.cpu._nombre.toolTip(), "CPU libre")
            self.assertEqual(ventana.bcp_ejecucion._valores[0].text(), "—")
            self.assertEqual(ventana.cpu._barra_quantum.value(), 0)
        finally:
            controlador.pausar()
            ventana.close()

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
            self.assertIsNone(ventana.controlador.motor.en_cpu)
            self.assertEqual(ventana.controlador.motor.buscar(101).tiempo_total, 15)
            self.assertEqual(len(ventana.controlador.motor.preparados), 1)
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
