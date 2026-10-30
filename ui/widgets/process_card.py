"""Tarjeta de un proceso dentro de una cola."""
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QVBoxLayout

from utils.formato import tooltip_proceso


class ProcessCard(QFrame):
    seleccionado = Signal(int)

    def __init__(self, p, parent=None):
        super().__init__(parent)
        self.setObjectName("Card")
        self.pid = p.pid
        self.setCursor(Qt.PointingHandCursor)
        # el color del proceso viene de utils/colors.py (PALETA_PROCESOS) a través de p.color

        self._badge = QLabel(p.letra)
        self._badge.setObjectName("Badge")
        self._badge.setFixedSize(34, 34)
        self._badge.setAlignment(Qt.AlignCenter)
        self._badge.setStyleSheet(f"QLabel#Badge {{ background: {p.color}; }}")

        self._nombre = QLabel()
        self._nombre.setTextFormat(Qt.PlainText)
        self._nombre.setWordWrap(True)
        self._nombre.setStyleSheet("font-weight: 600;")
        self._detalle = QLabel()
        self._detalle.setObjectName("Muted")
        textos = QVBoxLayout()
        textos.setSpacing(0)
        textos.addWidget(self._nombre)
        textos.addWidget(self._detalle)

        fila = QHBoxLayout(self)
        fila.setContentsMargins(10, 8, 10, 8)
        fila.addWidget(self._badge)
        fila.addLayout(textos, 1)
        self.actualizar(p)

    def actualizar(self, p):
        self._nombre.setText(p.nombre)
        self._detalle.setText(f"PID {p.pid}  ·  Prioridad {p.prioridad}  ·  {p.progreso_total}%")
        self.setToolTip(tooltip_proceso(p))

    def set_seleccionado(self, activo: bool):
        if self.property("sel") == activo:
            return
        self.setProperty("sel", activo)
        self.style().unpolish(self)
        self.style().polish(self)

    def mousePressEvent(self, e):
        self.seleccionado.emit(self.pid)
        super().mousePressEvent(e)
