"""Línea de tiempo de ejecución. Al pasar el mouse sobre una barra se muestra la info del proceso."""
from PySide6.QtCore import QRectF, Qt
from PySide6.QtGui import QColor, QPainter, QPen
from PySide6.QtWidgets import QScrollArea, QToolTip, QWidget, QHBoxLayout, QLabel, QPushButton, QCheckBox, QComboBox

from interfaz.estilos import colores
from interfaz.formato import formatear_milisegundos, tooltip_proceso

from .panel import Panel

MARGEN_IZQ, MARGEN_DER, MARGEN_SUP, MARGEN_INF = 66, 32, 34, 12
ALTO_FILA, ALTO_BARRA = 36, 24
PASOS = [100, 200, 500, 1000, 2000, 5000, 10000, 20000, 50000]


class _Lienzo(QWidget):
    def __init__(self, linea, buscar, parent=None):
        super().__init__(parent)
        self._linea = linea
        self._segmentos = []
        self._buscar = buscar          # pid -> Proceso | None
        self._filas: list[int] = []    # pids, en orden de primera aparición
        self._segmento_bajo_cursor = None
        self.reloj = 0
        self.escala = 0.16
        self.setMouseTracking(True)
        self.setMinimumHeight(MARGEN_SUP + ALTO_FILA + MARGEN_INF)

    def refrescar(self, reloj: int):
        self.reloj = reloj
        self._segmentos = list(self._linea.segmentos)
        identificadores_encontrados = {}
        for segmento in self._segmentos:
            identificadores_encontrados.setdefault(segmento.pid, None)
        self._filas = list(identificadores_encontrados)
        if not self._segmentos:
            self._segmento_bajo_cursor = None
        self.setMinimumHeight(MARGEN_SUP + max(1, len(self._filas)) * ALTO_FILA + MARGEN_INF)
        self.setMinimumWidth(int(MARGEN_IZQ + MARGEN_DER + max(1000, reloj) * self.escala))
        self.update()

    # ---------- geometría ----------
    def _rango(self) -> tuple[int, int]:
        return 0, max(self.reloj, int((self.width() - MARGEN_IZQ) / self.escala))

    def _posicion_horizontal(self, instante: float) -> float:
        return MARGEN_IZQ + instante * self.escala

    def _rectangulo_segmento(self, segmento) -> QRectF:
        fila = self._filas.index(segmento.pid)
        inicio_horizontal = self._posicion_horizontal(segmento.inicio)
        fin_horizontal = self._posicion_horizontal(segmento.fin)
        posicion_vertical = MARGEN_SUP + fila * ALTO_FILA + (ALTO_FILA - ALTO_BARRA) / 2
        return QRectF(inicio_horizontal, posicion_vertical, max(2.0, fin_horizontal - inicio_horizontal), ALTO_BARRA)

    def _segmento_en(self, posicion_cursor):
        inicio_visible, fin_visible = self._rango()
        for segmento in reversed(self._segmentos):
            if segmento.fin < inicio_visible or segmento.inicio > fin_visible:
                continue
            if self._rectangulo_segmento(segmento).contains(posicion_cursor):
                return segmento
        return None

    # ---------- eventos ----------
    def mouseMoveEvent(self, evento):
        segmento = self._segmento_en(evento.position())
        if segmento is not self._segmento_bajo_cursor:
            self._segmento_bajo_cursor = segmento
            self.update()
        if segmento is None:
            QToolTip.hideText()
            return
        proceso = self._buscar(segmento.pid)
        if proceso is not None:
            QToolTip.showText(evento.globalPosition().toPoint(), tooltip_proceso(proceso, segmento), self)

    def leaveEvent(self, evento):
        self._segmento_bajo_cursor = None
        QToolTip.hideText()
        self.update()

    # ---------- dibujo ----------
    def paintEvent(self, evento):
        pintor = QPainter(self)
        pintor.setRenderHint(QPainter.Antialiasing)
        pintor.fillRect(self.rect(), QColor(colores.GANTT_BG))
        inicio_visible = max(0, int((evento.rect().left() - MARGEN_IZQ) / self.escala))
        fin_visible = max(inicio_visible, int((evento.rect().right() - MARGEN_IZQ) / self.escala) + 1)
        alto_zona = MARGEN_SUP + max(1, len(self._filas)) * ALTO_FILA

        self._dibujar_fondo_filas(pintor)
        self._dibujar_eje_tiempo(pintor, inicio_visible, fin_visible, alto_zona)
        self._dibujar_identificadores(pintor)
        if not self._segmentos:
            pintor.drawText(self.rect(), Qt.AlignCenter, "Agrega procesos e inicia la simulación para ver su recorrido.")

        self._dibujar_segmentos(pintor, inicio_visible, fin_visible)
        self._dibujar_instante_actual(pintor, alto_zona)

    def _dibujar_fondo_filas(self, pintor):
        for fila in range(len(self._filas)):
            if fila % 2 == 0:
                pintor.fillRect(QRectF(0, MARGEN_SUP + fila * ALTO_FILA, self.width(), ALTO_FILA), QColor(colores.BG_PANEL))

    def _dibujar_eje_tiempo(self, pintor, inicio_visible, fin_visible, alto_zona):
        # rejilla + eje de tiempo
        # Separa las marcas al menos 85 píxeles para que los textos no se monten.
        paso = PASOS[-1]
        for intervalo_candidato in PASOS:
            if intervalo_candidato * self.escala >= 85:
                paso = intervalo_candidato
                break
        pintor.setFont(self.font())
        instante = (inicio_visible // paso) * paso
        while instante <= fin_visible:
            if instante >= inicio_visible:
                posicion_horizontal = self._posicion_horizontal(instante)
                pintor.setPen(QPen(QColor(colores.GANTT_GRID), 1))
                pintor.drawLine(int(posicion_horizontal), MARGEN_SUP, int(posicion_horizontal), alto_zona)
                pintor.setPen(QColor(colores.TEXT_MUTED))
                pintor.drawText(QRectF(posicion_horizontal - 38, 5, 76, 20), Qt.AlignCenter, formatear_milisegundos(instante))
            instante += paso

    def _dibujar_identificadores(self, pintor):
        # Cada fila muestra el PID de su proceso.
        pintor.setPen(QColor(colores.TEXT_MUTED))
        for indice_fila, pid in enumerate(self._filas):
            pintor.drawText(QRectF(4, MARGEN_SUP + indice_fila * ALTO_FILA, MARGEN_IZQ - 8, ALTO_FILA),
                       Qt.AlignVCenter | Qt.AlignLeft, str(pid))

    def _dibujar_segmentos(self, pintor, inicio_visible, fin_visible):
        # barras
        for segmento in self._segmentos:
            if segmento.fin < inicio_visible or segmento.inicio > fin_visible:
                continue
            rectangulo = self._rectangulo_segmento(segmento)
            pintor.setPen(Qt.NoPen)
            pintor.setBrush(QColor(colores.color_pid(segmento.pid)))
            pintor.drawRoundedRect(rectangulo, 6, 6)
            if rectangulo.width() > 18:
                proceso = self._buscar(segmento.pid)
                pintor.setPen(QColor(colores.TEXT_ON_ACCENT))
                pintor.drawText(rectangulo, Qt.AlignCenter, proceso.letra if proceso else "")
            if segmento is self._segmento_bajo_cursor:
                pintor.setPen(QPen(QColor(colores.GANTT_HOVER), 2))
                pintor.setBrush(Qt.NoBrush)
                pintor.drawRoundedRect(rectangulo, 6, 6)

    def _dibujar_instante_actual(self, pintor, alto_zona):
        # línea del "ahora"
        posicion_horizontal = self._posicion_horizontal(self.reloj)
        pintor.setPen(QPen(QColor(colores.GANTT_NOW), 1, Qt.DashLine))
        pintor.drawLine(int(posicion_horizontal), MARGEN_SUP, int(posicion_horizontal), alto_zona)


class HistorialCpu(Panel):
    def __init__(self, linea, buscar, parent=None):
        super().__init__("RECORRIDO DE CPU · HISTORIAL", parent)
        self._lienzo = _Lienzo(linea, buscar)
        self._ajustando = False
        controles = QHBoxLayout()
        boton_inicio = QPushButton("← Inicio")
        boton_inicio.setToolTip("Volver a los primeros eventos")
        boton_inicio.clicked.connect(self.ir_inicio)
        boton_ahora = QPushButton("Ahora →")
        boton_ahora.clicked.connect(self.ir_actual)
        self.seguir = QCheckBox("Seguir ejecución")
        self.seguir.setChecked(True)
        self.seguir.toggled.connect(self._seguir)
        self.zoom = QComboBox()
        for texto, escala in [("50 %", 0.08), ("100 %", 0.16), ("200 %", 0.32), ("400 %", 0.64)]:
            self.zoom.addItem(texto, escala)
        self.zoom.setCurrentIndex(1)
        self.zoom.currentIndexChanged.connect(self._zoom)
        controles.addWidget(boton_inicio)
        controles.addWidget(boton_ahora)
        controles.addStretch()
        controles.addWidget(self.seguir)
        controles.addWidget(QLabel("Zoom"))
        controles.addWidget(self.zoom)
        self.cuerpo.addLayout(controles)
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.scroll.setWidget(self._lienzo)
        self.scroll.horizontalScrollBar().valueChanged.connect(self._desplazado)
        self.scroll.horizontalScrollBar().rangeChanged.connect(self._rango_cambiado)
        self.cuerpo.addWidget(self.scroll, 1)
        ayuda = QLabel("Arrastra la barra horizontal para explorar · Pasa sobre un tramo para ver sus detalles")
        ayuda.setObjectName("Muted")
        self.cuerpo.addWidget(ayuda)

    def _desplazado(self, valor):
        barra_desplazamiento = self.scroll.horizontalScrollBar()
        if not self._ajustando and valor < barra_desplazamiento.maximum() - 4:
            self.seguir.setChecked(False)

    def _rango_cambiado(self, minimo, maximo):
        if self.seguir.isChecked():
            self._al_final()

    def _al_final(self):
        self._ajustando = True
        barra_desplazamiento = self.scroll.horizontalScrollBar()
        barra_desplazamiento.setValue(barra_desplazamiento.maximum())
        self._ajustando = False

    def _seguir(self, activo):
        if activo:
            self._al_final()

    def ir_inicio(self):
        self.seguir.setChecked(False)
        self.scroll.horizontalScrollBar().setValue(0)

    def ir_actual(self):
        self.seguir.setChecked(True)
        self._al_final()

    def _zoom(self):
        barra_desplazamiento = self.scroll.horizontalScrollBar()
        instante = max(0, (barra_desplazamiento.value() - MARGEN_IZQ) / self._lienzo.escala)
        self._lienzo.escala = self.zoom.currentData()
        self.refrescar(self._lienzo.reloj)
        if not self.seguir.isChecked():
            barra_desplazamiento.setValue(int(MARGEN_IZQ + instante * self._lienzo.escala))

    def refrescar(self, reloj: int):
        self._ajustando = True
        self._lienzo.refrescar(reloj)
        if reloj == 0:
            self.seguir.setChecked(True)
            self.scroll.horizontalScrollBar().setValue(0)
        elif self.seguir.isChecked():
            self._al_final()
        self._ajustando = False
