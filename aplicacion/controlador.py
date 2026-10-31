"""Coordina controles, reproducción y actualización de la vista."""
from PySide6.QtCore import QObject, Signal

from simulacion.motor import MotorSimulacion
from .temporizador import Temporizador


class ControladorSimulacion(QObject):
    cambio = Signal()
    segmento = Signal(object)
    evento = Signal(str)
    reiniciado = Signal()

    def __init__(self, parent=None, seed=None, motor=None):
        super().__init__(parent)
        self.motor = motor if motor is not None else MotorSimulacion(seed)
        self.temporizador = Temporizador(self.paso, self)
        self.seleccion = None
        self.vista = None

    @property
    def corriendo(self):
        return self.temporizador.isActive()

    def conectar_vista(self, vista):
        self.vista = vista
        barra_controles = vista.barra_controles
        barra_controles.alternar_panel_lateral.connect(self._actualizar_visibilidad_panel_lateral)
        barra_controles.iniciar.connect(self.iniciar)
        barra_controles.pausar.connect(self.pausar)
        barra_controles.paso.connect(self.paso)
        barra_controles.reiniciar.connect(self.reiniciar)
        barra_controles.divisor_quantum_cambiado.connect(self.cambiar_divisor_quantum)
        barra_controles.velocidad_cambiada.connect(self.set_velocidad)
        vista.formulario.enviar.connect(self.agregar_desde_formulario)
        vista.formulario.aleatorio.connect(self.agregar_aleatorio)
        for panel in (vista.preparados, vista.suspendidos, vista.terminados):
            panel.seleccionado.connect(self.seleccionar)
        self.cambio.connect(self.refrescar)
        self.evento.connect(vista.mostrar_evento)
        self.reiniciado.connect(vista.limpiar_eventos)
        self.refrescar()

    def _actualizar_visibilidad_panel_lateral(self):
        panel_visible = self.vista.barra_controles.formulario_visible()
        self.vista.panel_lateral.setVisible(panel_visible)

    def refrescar(self):
        if self.vista is not None:
            self.vista.mostrar(self.motor, self.seleccion, self.corriendo)

    def _publicar_eventos_y_estado(self):
        """Entrega los mensajes pendientes y solicita actualizar la pantalla."""
        for mensaje in self.motor.extraer_eventos():
            self.evento.emit(mensaje)
        self.segmento.emit(self.motor.linea.abierto)
        self.cambio.emit()

    def iniciar(self):
        if self.motor.hay_trabajo:
            self.temporizador.start()
        self.cambio.emit()

    def pausar(self):
        self.temporizador.stop()
        self.cambio.emit()

    def paso(self):
        self.motor.paso()
        if not self.motor.hay_trabajo:
            self.temporizador.stop()
        self._publicar_eventos_y_estado()

    def reiniciar(self):
        self.temporizador.stop()
        self.motor.reiniciar()
        self.seleccion = None
        self.reiniciado.emit()
        self._publicar_eventos_y_estado()

    def cambiar_divisor_quantum(self, divisor_quantum):
        self.motor.cambiar_divisor_quantum(divisor_quantum)
        self._publicar_eventos_y_estado()

    def set_velocidad(self, intervalo_ms):
        if intervalo_ms <= 0:
            raise ValueError("El intervalo debe ser positivo")
        self.temporizador.setInterval(intervalo_ms)

    def agregar_proceso(self, **datos):
        proceso = self.motor.agregar_proceso(**datos)
        self._publicar_eventos_y_estado()
        return proceso

    def agregar_desde_formulario(self):
        proceso = self.agregar_proceso(**self.vista.formulario.datos())
        self.seleccionar(proceso.pid)
        self.vista.formulario.limpiar()

    def agregar_aleatorio(self):
        proceso = self.motor.agregar_aleatorio(self.vista.formulario.nombre())
        self._publicar_eventos_y_estado()
        self.seleccionar(proceso.pid)
        self.vista.formulario.limpiar()

    def seleccionar(self, pid):
        self.seleccion = pid
        self.refrescar()
