"""Proceso que está usando la CPU y el avance de su quantum."""
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QHBoxLayout, QLabel, QProgressBar, QVBoxLayout

from interfaz.estilos import colores

from .panel import Panel
from .etiqueta_elidida import EtiquetaElidida


class PanelCpu(Panel):
    def __init__(self, parent=None):
        super().__init__("CPU / EJECUCIÓN ACTUAL", parent)
        self._etiqueta_identificador = QLabel("–")
        self._etiqueta_identificador.setObjectName("Badge")
        self._etiqueta_identificador.setFixedSize(72, 72)
        self._etiqueta_identificador.setAlignment(Qt.AlignCenter)
        self._etiqueta_identificador.setStyleSheet(f"QLabel#Badge {{ background: {colores.BORDER}; font-size: 28px; }}")

        self._nombre = EtiquetaElidida("CPU libre")
        self._nombre.setObjectName("Big")
        self._detalle = QLabel("Sin proceso en ejecución")
        self._detalle.setObjectName("Muted")
        textos = QVBoxLayout()
        textos.addStretch()
        textos.addWidget(self._nombre)
        textos.addWidget(self._detalle)
        textos.addStretch()

        fila = QHBoxLayout()
        fila.setSpacing(14)
        fila.addWidget(self._etiqueta_identificador)
        fila.addLayout(textos, 1)
        self.cuerpo.addLayout(fila)

        etiqueta = QLabel("Progreso del quantum")
        etiqueta.setObjectName("Muted")
        self._barra_quantum = QProgressBar()
        self._barra_quantum.setRange(0, 100)
        self._barra_quantum.setFixedHeight(16)
        self.cuerpo.addWidget(etiqueta)
        self.cuerpo.addWidget(self._barra_quantum)
        self._barra_progreso_total = QProgressBar()
        self._barra_progreso_total.setObjectName("TotalProgress")
        self._barra_progreso_total.setRange(0, 100)
        self._barra_progreso_total.setFixedHeight(16)
        self.cuerpo.addWidget(QLabel("Progreso total del proceso"))
        self.cuerpo.addWidget(self._barra_progreso_total)

    def actualizar(self, proceso):
        if proceso is None:
            self._etiqueta_identificador.setText("–")
            self._etiqueta_identificador.setStyleSheet(f"QLabel#Badge {{ background: {colores.BORDER}; font-size: 28px; }}")
            self._nombre.setText("CPU libre")
            self._detalle.setText("Sin proceso en ejecución")
            self._barra_quantum.setValue(0)
            self._barra_progreso_total.setValue(0)
            return
        self._etiqueta_identificador.setText(proceso.letra)
        self._etiqueta_identificador.setStyleSheet(f"QLabel#Badge {{ background: {colores.color_pid(proceso.pid)}; font-size: 28px; }}")
        self._nombre.setText(proceso.nombre)
        self._detalle.setText(f"PID {proceso.pid}  ·  Prioridad {proceso.prioridad}")
        self._barra_quantum.setValue(proceso.progreso_quantum)
        self._barra_progreso_total.setValue(proceso.progreso_total)
