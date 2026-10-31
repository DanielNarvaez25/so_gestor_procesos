"""Reloj de reproducción: no modifica las reglas del tiempo simulado."""
from PySide6.QtCore import QTimer

INTERVALO_REAL_MS = 100


class Temporizador(QTimer):
    def __init__(self, paso, parent=None):
        super().__init__(parent)
        self.setInterval(INTERVALO_REAL_MS)
        self.timeout.connect(paso)
