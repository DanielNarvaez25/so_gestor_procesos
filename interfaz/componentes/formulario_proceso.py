"""Creación manual y aleatoria de procesos."""
from PySide6.QtCore import Signal
from PySide6.QtWidgets import QComboBox, QHBoxLayout, QLabel, QLineEdit, QPushButton, QSpinBox, QVBoxLayout
from simulacion import configuracion
from .panel import Panel

class FormularioProceso(Panel):
    enviar = Signal()
    aleatorio = Signal()

    def __init__(self, parent=None):
        super().__init__("NUEVO PROCESO", parent)
        self._nombre = QLineEdit()
        self._nombre.setPlaceholderText("Ej. Compilar proyecto")
        self._nombre.setMaxLength(60)
        self._nombre.returnPressed.connect(self.enviar)
        self._prioridad = QComboBox()
        for prioridad in range(configuracion.PRIORIDAD_MIN, configuracion.PRIORIDAD_MAX + 1):
            texto_prioridad = str(prioridad)
            if prioridad == configuracion.PRIORIDAD_MAX:
                texto_prioridad += " · Alta"
            elif prioridad == configuracion.PRIORIDAD_MIN:
                texto_prioridad += " · Baja"
            self._prioridad.addItem(texto_prioridad, prioridad)
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
        for texto, control in [("Nombre · opcional", self._nombre), ("Prioridad", self._prioridad)]:
            self.cuerpo.addWidget(QLabel(texto))
            self.cuerpo.addWidget(control)
        distribucion_campos_numericos = QHBoxLayout()
        for texto, control in [("Tiempo de CPU", self._tiempo), ("E/S por turno", self._interactividad)]:
            distribucion_campo = QVBoxLayout()
            distribucion_campo.addWidget(QLabel(texto))
            distribucion_campo.addWidget(control)
            distribucion_campos_numericos.addLayout(distribucion_campo)
        self.cuerpo.addLayout(distribucion_campos_numericos)
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
        return {
            "nombre": self.nombre(),
            "prioridad": self.prioridad(),
            "tiempo_total": self._tiempo.value(),
            "interactividad": self._interactividad.value(),
        }

    def limpiar(self):
        self._nombre.clear()
