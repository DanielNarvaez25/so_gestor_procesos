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
        t = vista.toolbar
        t.alternar_form.connect(lambda: vista.sidebar.setVisible(t.formulario_visible()))
        t.iniciar.connect(self.iniciar)
        t.pausar.connect(self.pausar)
        t.paso.connect(self.paso)
        t.reiniciar.connect(self.reiniciar)
        t.rata_cambiada.connect(self.set_rata)
        t.velocidad_cambiada.connect(self.set_velocidad)
        vista.form.enviar.connect(self.agregar_desde_formulario)
        vista.form.aleatorio.connect(self.agregar_aleatorio)
        for panel in (vista.preparados, vista.suspendidos, vista.terminados,
                      vista.tabla_preparados, vista.tabla_suspendidos):
            panel.seleccionado.connect(self.seleccionar)
        self.cambio.connect(self.refrescar)
        self.evento.connect(vista.mostrar_evento)
        self.reiniciado.connect(vista.limpiar_eventos)
        self.refrescar()

    def refrescar(self):
        if self.vista is not None:
            self.vista.mostrar(self.motor, self.seleccion, self.corriendo)

    def _publicar(self):
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
        self._publicar()

    def reiniciar(self):
        self.temporizador.stop()
        self.motor.reiniciar()
        self.seleccion = None
        self.reiniciado.emit()
        self._publicar()

    def set_rata(self, rata):
        self.motor.set_rata(rata)
        self._publicar()

    def set_velocidad(self, intervalo_ms):
        if intervalo_ms <= 0:
            raise ValueError("El intervalo debe ser positivo")
        self.temporizador.setInterval(intervalo_ms)

    def agregar_proceso(self, **datos):
        proceso = self.motor.agregar_proceso(**datos)
        self._publicar()
        return proceso

    def agregar_desde_formulario(self):
        proceso = self.agregar_proceso(**self.vista.form.datos())
        self.seleccionar(proceso.pid)
        self.vista.form.limpiar()

    def agregar_aleatorio(self):
        proceso = self.motor.agregar_aleatorio(self.vista.form.nombre())
        self._publicar()
        self.seleccionar(proceso.pid)
        self.vista.form.limpiar()

    def seleccionar(self, pid):
        self.seleccion = pid
        self.refrescar()
