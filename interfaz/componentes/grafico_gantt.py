"""Línea de tiempo de ejecución. Al pasar el mouse sobre una barra se muestra la info del proceso."""
from PySide6.QtCore import QRectF, Qt
from PySide6.QtGui import QColor, QPainter, QPen
from PySide6.QtWidgets import QScrollArea, QToolTip, QWidget, QHBoxLayout, QLabel, QPushButton, QCheckBox, QComboBox

from interfaz.estilos import colores as colors
from interfaz.formato import ms, tooltip_proceso

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
        self._hover = None
        self.reloj = 0
        self.escala = 0.16
        self.setMouseTracking(True)
        self.setMinimumHeight(MARGEN_SUP + ALTO_FILA + MARGEN_INF)

    def refrescar(self, reloj: int):
        self.reloj = reloj
        self._segmentos = list(self._linea.segmentos)
        vistos = {}
        for s in self._segmentos:
            vistos.setdefault(s.pid, None)
        self._filas = list(vistos)
        if not self._segmentos:
            self._hover = None
        self.setMinimumHeight(MARGEN_SUP + max(1, len(self._filas)) * ALTO_FILA + MARGEN_INF)
        self.setMinimumWidth(int(MARGEN_IZQ + MARGEN_DER + max(1000, reloj) * self.escala))
        self.update()

    # ---------- geometría ----------
    def _rango(self) -> tuple[int, int]:
        return 0, max(self.reloj, int((self.width() - MARGEN_IZQ) / self.escala))

    def _x(self, t: float, t0: int = 0) -> float:
        return MARGEN_IZQ + t * self.escala

    def _rect(self, s, t0: int) -> QRectF:
        fila = self._filas.index(s.pid)
        x1, x2 = self._x(s.inicio), self._x(s.fin)
        y = MARGEN_SUP + fila * ALTO_FILA + (ALTO_FILA - ALTO_BARRA) / 2
        return QRectF(x1, y, max(2.0, x2 - x1), ALTO_BARRA)

    def _segmento_en(self, pos):
        t0, t1 = self._rango()
        for s in reversed(self._segmentos):
            if s.fin >= t0 and s.inicio <= t1 and self._rect(s, t0).contains(pos):
                return s
        return None

    # ---------- eventos ----------
    def mouseMoveEvent(self, e):
        s = self._segmento_en(e.position())
        if s is not self._hover:
            self._hover = s
            self.update()
        if s is None:
            QToolTip.hideText()
            return
        p = self._buscar(s.pid)
        if p is not None:
            QToolTip.showText(e.globalPosition().toPoint(), tooltip_proceso(p, s), self)

    def leaveEvent(self, e):
        self._hover = None
        QToolTip.hideText()
        self.update()

    # ---------- dibujo ----------
    def paintEvent(self, evento):
        g = QPainter(self)
        g.setRenderHint(QPainter.Antialiasing)
        g.fillRect(self.rect(), QColor(colors.GANTT_BG))
        t0 = max(0, int((evento.rect().left() - MARGEN_IZQ) / self.escala))
        t1 = max(t0, int((evento.rect().right() - MARGEN_IZQ) / self.escala) + 1)
        alto_zona = MARGEN_SUP + max(1, len(self._filas)) * ALTO_FILA

        for fila in range(len(self._filas)):
            if fila % 2 == 0:
                g.fillRect(QRectF(0, MARGEN_SUP + fila * ALTO_FILA, self.width(), ALTO_FILA), QColor(colors.BG_PANEL))

        # rejilla + eje de tiempo
        paso = next((s for s in PASOS if s * self.escala >= 85), PASOS[-1])
        g.setFont(self.font())
        t = (t0 // paso) * paso
        while t <= t1:
            if t >= t0:
                x = self._x(t, t0)
                g.setPen(QPen(QColor(colors.GANTT_GRID), 1))
                g.drawLine(int(x), MARGEN_SUP, int(x), alto_zona)
                g.setPen(QColor(colors.TEXT_MUTED))
                g.drawText(QRectF(x - 38, 5, 76, 20), Qt.AlignCenter, ms(t))
            t += paso

        # etiquetas de fila (PA, PB...)
        g.setPen(QColor(colors.TEXT_MUTED))
        for i, pid in enumerate(self._filas):
            p = self._buscar(pid)
            g.drawText(QRectF(4, MARGEN_SUP + i * ALTO_FILA, MARGEN_IZQ - 8, ALTO_FILA),
                       Qt.AlignVCenter | Qt.AlignLeft, str(pid))

        if not self._segmentos:
            g.drawText(self.rect(), Qt.AlignCenter, "Agrega procesos e inicia la simulación para ver su recorrido.")

        # barras
        for s in self._segmentos:
            if s.fin < t0 or s.inicio > t1:
                continue
            r = self._rect(s, t0)
            g.setPen(Qt.NoPen)
            g.setBrush(QColor(colors.color_pid(s.pid)))
            g.drawRoundedRect(r, 6, 6)
            if r.width() > 18:
                p = self._buscar(s.pid)
                g.setPen(QColor(colors.TEXT_ON_ACCENT))
                g.drawText(r, Qt.AlignCenter, p.letra if p else "")
            if s is self._hover:
                g.setPen(QPen(QColor(colors.GANTT_HOVER), 2))
                g.setBrush(Qt.NoBrush)
                g.drawRoundedRect(r, 6, 6)

        # línea del "ahora"
        x = self._x(self.reloj, t0)
        g.setPen(QPen(QColor(colors.GANTT_NOW), 1, Qt.DashLine))
        g.drawLine(int(x), MARGEN_SUP, int(x), alto_zona)


class GanttView(Panel):
    def __init__(self, linea, buscar, parent=None):
        super().__init__("RECORRIDO DE CPU · HISTORIAL", parent)
        self._lienzo = _Lienzo(linea, buscar)
        self._ajustando = False
        controles = QHBoxLayout()
        inicio = QPushButton("← Inicio")
        inicio.setToolTip("Volver a los primeros eventos")
        inicio.clicked.connect(self.ir_inicio)
        actual = QPushButton("Ahora →")
        actual.clicked.connect(self.ir_actual)
        self.seguir = QCheckBox("Seguir ejecución")
        self.seguir.setChecked(True)
        self.seguir.toggled.connect(self._seguir)
        self.zoom = QComboBox()
        for texto, escala in [("50 %", 0.08), ("100 %", 0.16), ("200 %", 0.32), ("400 %", 0.64)]:
            self.zoom.addItem(texto, escala)
        self.zoom.setCurrentIndex(1)
        self.zoom.currentIndexChanged.connect(self._zoom)
        controles.addWidget(inicio)
        controles.addWidget(actual)
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
        barra = self.scroll.horizontalScrollBar()
        if not self._ajustando and valor < barra.maximum() - 4:
            self.seguir.setChecked(False)

    def _rango_cambiado(self, minimo, maximo):
        if self.seguir.isChecked():
            self._al_final()

    def _al_final(self):
        self._ajustando = True
        barra = self.scroll.horizontalScrollBar()
        barra.setValue(barra.maximum())
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
        barra = self.scroll.horizontalScrollBar()
        instante = max(0, (barra.value() - MARGEN_IZQ) / self._lienzo.escala)
        self._lienzo.escala = self.zoom.currentData()
        self.refrescar(self._lienzo.reloj)
        if not self.seguir.isChecked():
            barra.setValue(int(MARGEN_IZQ + instante * self._lienzo.escala))

    def refrescar(self, reloj: int):
        self._ajustando = True
        self._lienzo.refrescar(reloj)
        if reloj == 0:
            self.seguir.setChecked(True)
            self.scroll.horizontalScrollBar().setValue(0)
        elif self.seguir.isChecked():
            self._al_final()
        self._ajustando = False
