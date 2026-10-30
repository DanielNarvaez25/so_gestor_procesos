"""Proceso que está usando la CPU y el avance de su quantum."""
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QHBoxLayout, QLabel, QProgressBar, QVBoxLayout

from utils import colors

from .panel import Panel


class CpuPanel(Panel):
    def __init__(self, parent=None):
        super().__init__("PROCESO EN CPU", parent)
        self._badge = QLabel("–")
        self._badge.setObjectName("Badge")
        self._badge.setFixedSize(72, 72)
        self._badge.setAlignment(Qt.AlignCenter)
        self._badge.setStyleSheet(f"QLabel#Badge {{ background: {colors.BORDER}; font-size: 28px; }}")

        self._nombre = QLabel("CPU libre")
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
        fila.addWidget(self._badge)
        fila.addLayout(textos, 1)
        self.cuerpo.addLayout(fila)

        etiqueta = QLabel("Progreso del quantum")
        etiqueta.setObjectName("Muted")
        self._barra = QProgressBar()
        self._barra.setRange(0, 100)
        self._barra.setFixedHeight(16)
        self.cuerpo.addWidget(etiqueta)
        self.cuerpo.addWidget(self._barra)

    def actualizar(self, p):
        if p is None:
            self._badge.setText("–")
            self._badge.setStyleSheet(f"QLabel#Badge {{ background: {colors.BORDER}; font-size: 28px; }}")
            self._nombre.setText("CPU libre")
            self._detalle.setText("Sin proceso en ejecución")
            self._barra.setValue(0)
            return
        self._badge.setText(p.letra)
        self._badge.setStyleSheet(f"QLabel#Badge {{ background: {p.color}; font-size: 28px; }}")
        self._nombre.setText(p.nombre)
        self._detalle.setText(f"PID {p.pid}  ·  Prioridad {p.prioridad}")
        self._barra.setValue(p.progreso_quantum)
