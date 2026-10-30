"""Creación manual y aleatoria de procesos."""
from PySide6.QtCore import Signal
from PySide6.QtWidgets import QComboBox, QHBoxLayout, QLabel, QLineEdit, QPushButton, QSpinBox, QVBoxLayout
from core import config
from .panel import Panel

class ProcessForm(Panel):
    enviar = Signal()
    aleatorio = Signal()

    def __init__(self, parent=None):
        super().__init__("NUEVO PROCESO", parent)
        self._nombre = QLineEdit()
        self._nombre.setPlaceholderText("Ej. Compilar proyecto")
        self._nombre.setMaxLength(60)
        self._nombre.returnPressed.connect(self.enviar)
        self._prioridad = QComboBox()
        for n in range(config.PRIORIDAD_MIN, config.PRIORIDAD_MAX + 1):
            self._prioridad.addItem(f"{n}" + (" · Alta" if n == 5 else " · Baja" if n == 1 else ""), n)
        self._prioridad.setCurrentIndex(self._prioridad.findData(3))
        self._tiempo = QSpinBox()
        self._tiempo.setRange(1, 60000)
        self._tiempo.setSingleStep(100)
        self._tiempo.setSuffix(" ms")
        self._tiempo.setValue(1000)
        self._interactividad = QSpinBox()
        self._interactividad.setRange(0, 100)
        self._interactividad.setSuffix(" %")
        self._interactividad.setValue(30)
        self._interactividad.setToolTip("Probabilidad de solicitar E/S en cada turno de CPU")
        for text, widget in [("Nombre · opcional", self._nombre), ("Prioridad", self._prioridad)]:
            self.cuerpo.addWidget(QLabel(text))
            self.cuerpo.addWidget(widget)
        row = QHBoxLayout()
        for text, widget in [("Tiempo de CPU", self._tiempo), ("E/S por turno", self._interactividad)]:
            col = QVBoxLayout()
            col.addWidget(QLabel(text))
            col.addWidget(widget)
            row.addLayout(col)
        self.cuerpo.addLayout(row)
        self.agregar = QPushButton("+  Agregar proceso")
        self.agregar.setObjectName("Primary")
        self.agregar.clicked.connect(self.enviar)
        self.generar = QPushButton("Generar aleatorio")
        self.generar.clicked.connect(self.aleatorio)
        self.cuerpo.addWidget(self.agregar)
        self.cuerpo.addWidget(self.generar)

    def nombre(self):
        return self._nombre.text().strip()

    def prioridad(self):
        return self._prioridad.currentData()

    def datos(self):
        return dict(nombre=self.nombre(), prioridad=self.prioridad(), tiempo_total=self._tiempo.value(), interactividad=self._interactividad.value())

    def limpiar(self):
        self._nombre.clear()
