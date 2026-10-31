from interfaz.estilos import colores
"""Tarjeta de un proceso dentro de una cola."""
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QVBoxLayout

from interfaz.formato import tooltip_proceso


class TarjetaProceso(QFrame):
    seleccionado = Signal(int)

    def __init__(self, proceso, parent=None):
        super().__init__(parent)
        self.setObjectName("Card")
        self.pid = proceso.pid
        self.setCursor(Qt.PointingHandCursor)
        # el color del proceso viene de interfaz/estilos/colores.py (PALETA_PROCESOS) a través de colors.color_pid(p.pid)

        self._etiqueta_identificador = QLabel(proceso.letra)
        self._etiqueta_identificador.setObjectName("Badge")
        self._etiqueta_identificador.setFixedSize(34, 34)
        self._etiqueta_identificador.setAlignment(Qt.AlignCenter)
        self._etiqueta_identificador.setStyleSheet(f"QLabel#Badge {{ background: {colores.color_pid(proceso.pid)}; }}")

        self._nombre = QLabel()
        self._nombre.setTextFormat(Qt.PlainText)
        self._nombre.setWordWrap(True)
        self._nombre.setStyleSheet("font-weight: 600;")
        self._detalle = QLabel()
        self._detalle.setObjectName("Muted")
        distribucion_textos = QVBoxLayout()
        distribucion_textos.setSpacing(0)
        distribucion_textos.addWidget(self._nombre)
        distribucion_textos.addWidget(self._detalle)

        distribucion_tarjeta = QHBoxLayout(self)
        distribucion_tarjeta.setContentsMargins(10, 8, 10, 8)
        distribucion_tarjeta.addWidget(self._etiqueta_identificador)
        distribucion_tarjeta.addLayout(distribucion_textos, 1)
        self.actualizar(proceso)

    def actualizar(self, proceso):
        self._nombre.setText(proceso.nombre)
        self._detalle.setText(f"PID {proceso.pid}  ·  Prioridad {proceso.prioridad}  ·  {proceso.progreso_total}%")
        self.setToolTip(tooltip_proceso(proceso))

    def set_seleccionado(self, activo: bool):
        if self.property("sel") == activo:
            return
        self.setProperty("sel", activo)
        self.style().unpolish(self)
        self.style().polish(self)

    def mousePressEvent(self, evento):
        self.seleccionado.emit(self.pid)
        super().mousePressEvent(evento)
