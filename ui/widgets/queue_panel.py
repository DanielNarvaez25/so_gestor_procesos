"""Cola de procesos (Preparados / Ejecución / Suspendidos) como lista de tarjetas."""
from PySide6.QtCore import Signal
from PySide6.QtWidgets import QLabel, QScrollArea, QVBoxLayout, QWidget

from .panel import Panel
from .process_card import ProcessCard


class QueuePanel(Panel):
    seleccionado = Signal(int)

    def __init__(self, titulo: str, vacio: str = "Sin procesos", conteo: bool = True, parent=None):
        super().__init__(titulo, parent)
        self._base = titulo
        self._conteo = conteo
        self._tarjetas: dict[int, ProcessCard] = {}

        self._lista = QVBoxLayout()
        self._lista.setContentsMargins(0, 0, 0, 0)
        self._lista.setSpacing(6)
        self._vacio = QLabel(vacio)
        self._vacio.setObjectName("Muted")
        self._lista.addWidget(self._vacio)
        self._lista.addStretch()

        contenedor = QWidget()
        contenedor.setLayout(self._lista)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(contenedor)
        scroll.viewport().setAutoFillBackground(False)
        contenedor.setAutoFillBackground(False)
        self.cuerpo.addWidget(scroll, 1)

    def actualizar(self, procesos, seleccionado: int | None = None):
        pids = {p.pid for p in procesos}
        for pid in [k for k in self._tarjetas if k not in pids]:
            tarjeta = self._tarjetas.pop(pid)
            self._lista.removeWidget(tarjeta)
            tarjeta.hide()
            tarjeta.deleteLater()

        for i, p in enumerate(procesos):
            tarjeta = self._tarjetas.get(p.pid)
            if tarjeta is None:
                tarjeta = ProcessCard(p)
                tarjeta.seleccionado.connect(self.seleccionado)
                self._tarjetas[p.pid] = tarjeta
            if self._lista.indexOf(tarjeta) != i:
                self._lista.removeWidget(tarjeta)
                self._lista.insertWidget(i, tarjeta)
            tarjeta.actualizar(p)
            tarjeta.set_seleccionado(p.pid == seleccionado)

        self._vacio.setVisible(not procesos)
        if self._conteo:
            self.set_titulo(f"{self._base} ({len(procesos)})")
