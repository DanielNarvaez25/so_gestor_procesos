"""Barra superior: agregar proceso, iniciar/pausar y rata de quantum."""
from PySide6.QtCore import Signal
from PySide6.QtWidgets import QComboBox, QFrame, QHBoxLayout, QLabel, QPushButton

from core import config


class Toolbar(QFrame):
    alternar_form = Signal()
    agregar = Signal()
    iniciar = Signal()
    pausar = Signal()
    reiniciar = Signal()
    rata_cambiada = Signal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("Panel")

        titulo = QLabel("GESTOR DE PROCESOS")
        titulo.setObjectName("Title")

        self._form = QPushButton("←")
        self._form.setToolTip("Mostrar / ocultar el formulario")
        self._form.clicked.connect(self.alternar_form)

        agregar = QPushButton("+ Agregar proceso")
        agregar.setObjectName("Primary")
        agregar.clicked.connect(self.agregar)

        self._play = QPushButton("▶ Iniciar")
        self._play.clicked.connect(self.iniciar)
        self._pausa = QPushButton("⏸ Pausar")
        self._pausa.clicked.connect(self.pausar)
        reiniciar = QPushButton("⟲ Reiniciar")
        reiniciar.clicked.connect(self.reiniciar)

        self._rata = QComboBox()
        for r in config.RATAS_QUANTUM:
            self._rata.addItem(str(r), r)
        self._rata.setCurrentIndex(self._rata.findData(config.RATA_POR_DEFECTO))
        self._rata.currentIndexChanged.connect(lambda _: self.rata_cambiada.emit(self._rata.currentData()))

        fila = QHBoxLayout(self)
        fila.setContentsMargins(12, 8, 12, 8)
        fila.addWidget(titulo)
        fila.addSpacing(16)
        for w in (self._form, agregar, self._play, self._pausa, reiniciar):
            fila.addWidget(w)
        fila.addStretch()
        fila.addWidget(QLabel("Rata de quantum"))
        fila.addWidget(self._rata)
        self.set_corriendo(False)

    def set_corriendo(self, corriendo: bool):
        self._play.setEnabled(not corriendo)
        self._pausa.setEnabled(corriendo)
