from aplicacion.temporizador import INTERVALO_REAL_MS
"""Controles de reproducción y configuración de la simulación."""
from PySide6.QtCore import Signal
from PySide6.QtWidgets import QComboBox, QFrame, QHBoxLayout, QLabel, QPushButton
from simulacion import configuracion as config

class Toolbar(QFrame):
    alternar_form = Signal()
    iniciar = Signal()
    pausar = Signal()
    reiniciar = Signal()
    paso = Signal()
    rata_cambiada = Signal(int)
    velocidad_cambiada = Signal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("Toolbar")
        self._form = QPushButton("Panel lateral")
        self._form.setCheckable(True)
        self._form.setChecked(True)
        self._form.clicked.connect(self.alternar_form)
        self._play = QPushButton("▶  Iniciar")
        self._play.setObjectName("Primary")
        self._play.clicked.connect(self.iniciar)
        self._pausa = QPushButton("Ⅱ  Pausar")
        self._pausa.clicked.connect(self.pausar)
        self._paso = QPushButton("Paso +10 ms")
        self._paso.setToolTip("Avanza hasta 10 ms simulados mientras está en pausa")
        self._paso.clicked.connect(self.paso)
        reset = QPushButton("Reiniciar")
        reset.setObjectName("Danger")
        reset.clicked.connect(self.reiniciar)
        self._rata = QComboBox()
        for r in config.RATAS_QUANTUM:
            self._rata.addItem(f"÷ {r}", r)
        self._rata.setCurrentIndex(self._rata.findData(config.RATA_POR_DEFECTO))
        self._rata.setToolTip("Quantum = tiempo total ÷ rata. Los cambios aplican al próximo turno.")
        self._rata.currentIndexChanged.connect(lambda _: self.rata_cambiada.emit(self._rata.currentData()))
        self._velocidad = QComboBox()
        for text, interval in [("0,5×", 200), ("1×", INTERVALO_REAL_MS), ("2×", 50), ("4×", 25)]:
            self._velocidad.addItem(text, interval)
        self._velocidad.setCurrentIndex(1)
        self._velocidad.setToolTip("Velocidad de reproducción; no cambia los tiempos simulados")
        self._velocidad.currentIndexChanged.connect(lambda _: self.velocidad_cambiada.emit(self._velocidad.currentData()))
        row = QHBoxLayout(self)
        row.setContentsMargins(12, 10, 12, 10)
        row.setSpacing(8)
        for w in (self._play, self._pausa, self._paso, reset):
            row.addWidget(w)
        row.addStretch()
        row.addWidget(QLabel("Quantum"))
        row.addWidget(self._rata)
        row.addSpacing(8)
        row.addWidget(QLabel("Velocidad"))
        row.addWidget(self._velocidad)
        row.addWidget(self._form)
        self.set_corriendo(False)

    def set_corriendo(self, corriendo, hay_trabajo=True):
        self._play.setEnabled(not corriendo and hay_trabajo)
        self._pausa.setEnabled(corriendo)
        self._paso.setEnabled(not corriendo and hay_trabajo)

    def formulario_visible(self):
        return self._form.isChecked()
