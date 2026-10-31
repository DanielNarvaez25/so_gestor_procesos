"""Cola de procesos (Preparados / Ejecución / Suspendidos) como lista de tarjetas."""
from PySide6.QtCore import Signal
from PySide6.QtWidgets import QLabel, QScrollArea, QVBoxLayout, QWidget

from .panel import Panel
from .tarjeta_proceso import TarjetaProceso


class PanelColas(Panel):
    seleccionado = Signal(int)

    def __init__(self, titulo: str, vacio: str = "Sin procesos", conteo: bool = True, parent=None):
        super().__init__(titulo, parent)
        self._base = titulo
        self._conteo = conteo
        self._tarjetas: dict[int, TarjetaProceso] = {}

        self._lista = QVBoxLayout()
        self._lista.setContentsMargins(0, 0, 0, 0)
        self._lista.setSpacing(6)
        self._vacio = QLabel(vacio)
        self._vacio.setObjectName("Muted")
        self._vacio.setWordWrap(True)
        self._lista.addWidget(self._vacio)
        self._lista.addStretch()

        contenedor = QWidget()
        contenedor.setLayout(self._lista)
        area_desplazamiento = QScrollArea()
        area_desplazamiento.setWidgetResizable(True)
        area_desplazamiento.setWidget(contenedor)
        area_desplazamiento.viewport().setAutoFillBackground(False)
        contenedor.setAutoFillBackground(False)
        self.cuerpo.addWidget(area_desplazamiento, 1)

    def actualizar(self, procesos, seleccionado: int | None = None):
        identificadores_actuales = {proceso.pid for proceso in procesos}
        # Se toma una copia de las claves antes de borrar tarjetas del diccionario.
        for pid in tuple(self._tarjetas):
            if pid in identificadores_actuales:
                continue
            tarjeta = self._tarjetas.pop(pid)
            self._lista.removeWidget(tarjeta)
            tarjeta.hide()
            tarjeta.deleteLater()

        for indice_tarjeta, proceso in enumerate(procesos):
            tarjeta = self._tarjetas.get(proceso.pid)
            if tarjeta is None:
                tarjeta = TarjetaProceso(proceso)
                tarjeta.seleccionado.connect(self.seleccionado)
                self._tarjetas[proceso.pid] = tarjeta
            if self._lista.indexOf(tarjeta) != indice_tarjeta:
                self._lista.removeWidget(tarjeta)
                self._lista.insertWidget(indice_tarjeta, tarjeta)
            tarjeta.actualizar(proceso)
            tarjeta.set_seleccionado(proceso.pid == seleccionado)

        self._vacio.setVisible(not procesos)
        if self._conteo:
            self.set_titulo(f"{self._base} ({len(procesos)})")
