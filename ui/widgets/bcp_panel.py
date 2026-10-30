"""Panel de detalle de un BCP (pares etiqueta / valor)."""
from PySide6.QtWidgets import QGridLayout, QLabel

from .bcp_campos import Campo
from .panel import Panel


class BcpPanel(Panel):
    def __init__(self, titulo: str, campos: list[Campo], columnas: int = 1, parent=None):
        super().__init__(titulo, parent)
        self._campos = campos
        self._valores: list[QLabel] = []
        grid = QGridLayout()
        grid.setHorizontalSpacing(10)
        grid.setVerticalSpacing(6)
        for i, campo in enumerate(campos):
            fila, col = divmod(i, columnas)
            etiqueta = QLabel(campo.etiqueta)
            etiqueta.setObjectName("Muted")
            valor = QLabel("—")
            grid.addWidget(etiqueta, fila, col * 2)
            grid.addWidget(valor, fila, col * 2 + 1)
            self._valores.append(valor)
        for c in range(columnas):
            grid.setColumnStretch(c * 2 + 1, 1)
        self.cuerpo.addLayout(grid)
        self.cuerpo.addStretch()

    def actualizar(self, p):
        for campo, label in zip(self._campos, self._valores):
            if p is None:
                label.setText("—")
                label.setStyleSheet("")
                continue
            label.setText(campo.valor(p))
            label.setStyleSheet(f"color: {campo.color(p)}; font-weight: 600;" if campo.color else "")
