"""Indicadores de estado de la simulación."""
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QVBoxLayout, QWidget
from interfaz.estilos import colores
from interfaz.formato import formatear_milisegundos

class ResumenSimulacion(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        distribucion_indicadores = QHBoxLayout(self)
        distribucion_indicadores.setContentsMargins(0, 0, 0, 0)
        distribucion_indicadores.setSpacing(10)
        self.valores = []
        for titulo, color in [("RELOJ SIMULADO", colores.TEXT), ("PREPARADOS", colores.STATE_PREPARADO), ("EN E/S", colores.STATE_SUSPENDIDO), ("TERMINADOS", colores.STATE_TERMINADO)]:
            tarjeta = QFrame()
            tarjeta.setObjectName("Metric")
            tarjeta.setStyleSheet(f"QFrame#Metric {{ border-top: 3px solid {color}; }}")
            distribucion_tarjeta = QVBoxLayout(tarjeta)
            distribucion_tarjeta.setContentsMargins(18, 12, 18, 12)
            etiqueta = QLabel(titulo)
            etiqueta.setObjectName("PanelTitle")
            valor = QLabel("0")
            valor.setObjectName("MetricValue")
            valor.setStyleSheet(f"color: {color};")
            distribucion_tarjeta.addWidget(etiqueta)
            distribucion_tarjeta.addWidget(valor)
            self.valores.append(valor)
            distribucion_indicadores.addWidget(tarjeta, 1)

    def actualizar(self, motor):
        for etiqueta, valor in zip(self.valores, [formatear_milisegundos(motor.reloj), len(motor.preparados), len(motor.suspendidos), len(motor.terminados)]):
            etiqueta.setText(str(valor))
