"""Indicadores de estado de la simulación."""
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QVBoxLayout, QWidget
from utils import colors
from utils.formato import ms

class Summary(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        row = QHBoxLayout(self)
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(10)
        self.valores = []
        for title, color in [("RELOJ SIMULADO", colors.TEXT), ("PREPARADOS", colors.STATE_PREPARADO), ("EN E/S", colors.STATE_SUSPENDIDO), ("TERMINADOS", colors.STATE_TERMINADO)]:
            card = QFrame()
            card.setObjectName("Metric")
            box = QVBoxLayout(card)
            box.setContentsMargins(16, 10, 16, 10)
            label = QLabel(title)
            label.setObjectName("PanelTitle")
            value = QLabel("0")
            value.setObjectName("MetricValue")
            value.setStyleSheet(f"color: {color};")
            box.addWidget(label)
            box.addWidget(value)
            self.valores.append(value)
            row.addWidget(card, 1)

    def actualizar(self, sim):
        for label, value in zip(self.valores, [ms(sim.reloj), len(sim.preparados), len(sim.suspendidos), len(sim.terminados)]):
            label.setText(str(value))
