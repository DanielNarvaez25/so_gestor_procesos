"""Formulario lateral: nombre y prioridad del nuevo proceso."""
from PySide6.QtCore import Signal
from PySide6.QtWidgets import QComboBox, QLabel, QLineEdit, QPushButton

from core import config

from .panel import Panel


class ProcessForm(Panel):
    enviar = Signal()      # Enter en el campo nombre
    aleatorio = Signal()   # botón "Generar aleatorio"

    def __init__(self, parent=None):
        super().__init__("NUEVO PROCESO", parent)
        self._nombre = QLineEdit()
        self._nombre.setPlaceholderText("Automático si se deja vacío")
        self._nombre.returnPressed.connect(self.enviar)

        self._prioridad = QComboBox()
        for n in range(config.PRIORIDAD_MIN, config.PRIORIDAD_MAX + 1):
            self._prioridad.addItem(str(n), n)
        self._prioridad.setCurrentIndex(self._prioridad.findData(3))

        cancelar = QPushButton("Cancelar")
        cancelar.clicked.connect(self.limpiar)
        generar = QPushButton("Generar aleatorio")
        generar.clicked.connect(self.aleatorio)

        self.cuerpo.addWidget(QLabel("Nombre del proceso"))
        self.cuerpo.addWidget(self._nombre)
        self.cuerpo.addWidget(QLabel(f"Prioridad ({config.PRIORIDAD_MIN}-{config.PRIORIDAD_MAX})"))
        self.cuerpo.addWidget(self._prioridad)
        self.cuerpo.addSpacing(8)
        self.cuerpo.addWidget(cancelar)
        self.cuerpo.addWidget(generar)
        self.cuerpo.addStretch()

    def nombre(self) -> str:
        return self._nombre.text().strip()

    def prioridad(self) -> int:
        return self._prioridad.currentData()

    def limpiar(self):
        self._nombre.clear()
        self._prioridad.setCurrentIndex(self._prioridad.findData(3))
