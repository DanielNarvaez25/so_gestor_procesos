"""Controles de reproducción y configuración de la simulación."""
from aplicacion.temporizador import INTERVALO_REAL_MS
from PySide6.QtCore import Signal
from PySide6.QtWidgets import QComboBox, QFrame, QHBoxLayout, QLabel, QPushButton
from simulacion import configuracion

class BarraControles(QFrame):
    alternar_panel_lateral = Signal()
    iniciar = Signal()
    pausar = Signal()
    reiniciar = Signal()
    paso = Signal()
    divisor_quantum_cambiado = Signal(int)
    velocidad_cambiada = Signal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("Toolbar")
        self._boton_panel_lateral = QPushButton("Panel lateral")
        self._boton_panel_lateral.setCheckable(True)
        self._boton_panel_lateral.setChecked(True)
        self._boton_panel_lateral.clicked.connect(self.alternar_panel_lateral)
        self._boton_iniciar = QPushButton("▶  Iniciar")
        self._boton_iniciar.setObjectName("Primary")
        self._boton_iniciar.clicked.connect(self.iniciar)
        self._boton_pausar = QPushButton("Ⅱ  Pausar")
        self._boton_pausar.clicked.connect(self.pausar)
        self._boton_paso = QPushButton("Paso +10 ms")
        self._boton_paso.setToolTip("Avanza hasta 10 ms simulados mientras está en pausa")
        self._boton_paso.clicked.connect(self.paso)
        boton_reiniciar = QPushButton("Reiniciar")
        boton_reiniciar.setObjectName("Danger")
        boton_reiniciar.clicked.connect(self.reiniciar)
        self._selector_divisor_quantum = QComboBox()
        for divisor_quantum in configuracion.DIVISORES_QUANTUM:
            self._selector_divisor_quantum.addItem(f"÷ {divisor_quantum}", divisor_quantum)
        self._selector_divisor_quantum.setCurrentIndex(self._selector_divisor_quantum.findData(configuracion.DIVISOR_QUANTUM_POR_DEFECTO))
        self._selector_divisor_quantum.setToolTip("Quantum = tiempo total ÷ rata. Los cambios aplican al próximo turno.")
        self._selector_divisor_quantum.currentIndexChanged.connect(self._notificar_cambio_divisor)
        self._selector_velocidad = QComboBox()
        for texto, intervalo_real in [("0,5×", 200), ("1×", INTERVALO_REAL_MS), ("2×", 50), ("4×", 25)]:
            self._selector_velocidad.addItem(texto, intervalo_real)
        self._selector_velocidad.setCurrentIndex(1)
        self._selector_velocidad.setToolTip("Velocidad de reproducción; no cambia los tiempos simulados")
        self._selector_velocidad.currentIndexChanged.connect(self._notificar_cambio_velocidad)
        distribucion_controles = QHBoxLayout(self)
        distribucion_controles.setContentsMargins(12, 10, 12, 10)
        distribucion_controles.setSpacing(8)
        for boton in (self._boton_iniciar, self._boton_pausar, self._boton_paso, boton_reiniciar):
            distribucion_controles.addWidget(boton)
        distribucion_controles.addStretch()
        distribucion_controles.addWidget(QLabel("Quantum"))
        distribucion_controles.addWidget(self._selector_divisor_quantum)
        distribucion_controles.addSpacing(8)
        distribucion_controles.addWidget(QLabel("Velocidad"))
        distribucion_controles.addWidget(self._selector_velocidad)
        distribucion_controles.addWidget(self._boton_panel_lateral)
        self.set_corriendo(False)

    def set_corriendo(self, corriendo, hay_trabajo=True):
        self._boton_iniciar.setEnabled(not corriendo and hay_trabajo)
        self._boton_pausar.setEnabled(corriendo)
        self._boton_paso.setEnabled(not corriendo and hay_trabajo)

    def formulario_visible(self):
        return self._boton_panel_lateral.isChecked()

    def _notificar_cambio_divisor(self):
        divisor_seleccionado = self._selector_divisor_quantum.currentData()
        self.divisor_quantum_cambiado.emit(divisor_seleccionado)

    def _notificar_cambio_velocidad(self):
        intervalo_seleccionado = self._selector_velocidad.currentData()
        self.velocidad_cambiada.emit(intervalo_seleccionado)
