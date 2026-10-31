"""Panel de detalle de un BCP (pares etiqueta / valor)."""
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QGridLayout, QLabel

from .bcp_campos import Campo
from .panel import Panel


class PanelBcp(Panel):
    def __init__(self, titulo: str, campos: list[Campo], columnas: int = 1, parent=None):
        super().__init__(titulo, parent)
        self._campos = campos
        self._valores: list[QLabel] = []
        cuadricula = QGridLayout()
        cuadricula.setHorizontalSpacing(10)
        cuadricula.setVerticalSpacing(6)
        for indice_campo, campo in enumerate(campos):
            fila, columna = divmod(indice_campo, columnas)
            etiqueta = QLabel(campo.etiqueta)
            etiqueta.setObjectName("Muted")
            valor = QLabel("—")
            valor.setTextFormat(Qt.PlainText)
            valor.setMinimumWidth(0)
            valor.setWordWrap(True)
            cuadricula.addWidget(etiqueta, fila, columna * 2)
            cuadricula.addWidget(valor, fila, columna * 2 + 1)
            self._valores.append(valor)
        for indice_columna in range(columnas):
            cuadricula.setColumnStretch(indice_columna * 2 + 1, 1)
        self.cuerpo.addLayout(cuadricula)
        self.cuerpo.addStretch()

    def actualizar(self, proceso):
        for campo, etiqueta_valor in zip(self._campos, self._valores):
            if proceso is None:
                etiqueta_valor.setText("—")
                etiqueta_valor.setStyleSheet("")
                continue
            etiqueta_valor.setText(campo.valor(proceso))
            etiqueta_valor.setStyleSheet(f"color: {campo.color(proceso)}; font-weight: 600;" if campo.color else "")
