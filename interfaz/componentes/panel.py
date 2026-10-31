"""Contenedor base"""
from PySide6.QtWidgets import QFrame, QLabel, QVBoxLayout


class Panel(QFrame):
    def __init__(self, titulo: str = "", parent=None):
        super().__init__(parent)
        self.setObjectName("Panel")
        self.cuerpo = QVBoxLayout(self)
        self.cuerpo.setContentsMargins(12, 10, 12, 12)
        self.cuerpo.setSpacing(8)
        self._titulo = QLabel(titulo)
        self._titulo.setObjectName("PanelTitle")
        self.cuerpo.addWidget(self._titulo)
        self._titulo.setVisible(bool(titulo))

    def set_titulo(self, texto: str):
        self._titulo.setText(texto)
