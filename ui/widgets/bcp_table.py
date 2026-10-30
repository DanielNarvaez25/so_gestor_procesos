"""Tabla de BCPs (Preparados / Suspendidos)."""
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QAbstractItemView, QHeaderView, QTableWidget, QTableWidgetItem

from utils import colors

from .bcp_campos import Campo
from .panel import Panel


class BcpTable(Panel):
    seleccionado = Signal(int)   # pid de la fila clicada

    def __init__(self, titulo: str, columnas: list[Campo], parent=None):
        super().__init__(titulo, parent)
        self._base = titulo
        self._columnas = columnas
        t = self.tabla = QTableWidget(0, len(columnas))
        t.setHorizontalHeaderLabels([c.etiqueta for c in columnas])
        t.verticalHeader().setVisible(False)
        cab = t.horizontalHeader()
        cab.setSectionResizeMode(QHeaderView.ResizeToContents)
        cab.setStretchLastSection(True)
        cab.setDefaultAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        t.setEditTriggers(QAbstractItemView.NoEditTriggers)
        t.setSelectionMode(QAbstractItemView.SingleSelection)
        t.setSelectionBehavior(QAbstractItemView.SelectRows)
        t.setAlternatingRowColors(True)
        t.verticalHeader().setDefaultSectionSize(34)
        t.setFocusPolicy(Qt.NoFocus)
        t.setShowGrid(False)
        t.cellClicked.connect(self._clic)
        self.cuerpo.addWidget(t)

    def _clic(self, fila: int, _col: int):
        item = self.tabla.item(fila, 0)
        if item:
            self.seleccionado.emit(item.data(Qt.UserRole))

    def actualizar(self, procesos):
        t = self.tabla
        t.setRowCount(len(procesos))
        for r, p in enumerate(procesos):
            for c, campo in enumerate(self._columnas):
                item = t.item(r, c)
                if item is None:
                    item = QTableWidgetItem()
                    t.setItem(r, c, item)
                item.setText(campo.valor(p))
                item.setForeground(QColor(campo.color(p) if campo.color else colors.TEXT))
                item.setData(Qt.UserRole, p.pid)
        self.set_titulo(f"{self._base} ({len(procesos)})")
