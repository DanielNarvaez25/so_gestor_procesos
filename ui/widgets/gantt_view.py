"""Línea de tiempo de ejecución. Al pasar el mouse sobre una barra se muestra la info del proceso."""
from PySide6.QtCore import QRectF, Qt
from PySide6.QtGui import QColor, QPainter, QPen
from PySide6.QtWidgets import QScrollArea, QToolTip, QWidget

from core import config
from utils import colors
from utils.formato import ms, tooltip_proceso

from .panel import Panel

MARGEN_IZQ, MARGEN_DER, MARGEN_SUP, MARGEN_INF = 66, 32, 14, 28
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
        self.update()

    # ---------- geometría ----------
    def _rango(self) -> tuple[int, int]:
        v = config.GANTT_VENTANA_MS
        t0 = max(0, self.reloj - v)
        return t0, t0 + v

    def _x(self, t: float, t0: int) -> float:
        ancho = max(1, self.width() - MARGEN_IZQ - MARGEN_DER)
        return MARGEN_IZQ + (t - t0) / config.GANTT_VENTANA_MS * ancho

    def _rect(self, s, t0: int) -> QRectF:
        fila = self._filas.index(s.pid)
        x1, x2 = self._x(max(s.inicio, t0), t0), self._x(min(s.fin, t0 + config.GANTT_VENTANA_MS), t0)
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
    def paintEvent(self, _):
        g = QPainter(self)
        g.setRenderHint(QPainter.Antialiasing)
        g.fillRect(self.rect(), QColor(colors.GANTT_BG))
        t0, t1 = self._rango()
        alto_zona = MARGEN_SUP + max(1, len(self._filas)) * ALTO_FILA

        # rejilla + eje de tiempo
        paso = next((s for s in PASOS if config.GANTT_VENTANA_MS / s <= 10), PASOS[-1])
        g.setFont(self.font())
        t = (t0 // paso) * paso
        while t <= t1:
            if t >= t0:
                x = self._x(t, t0)
                g.setPen(QPen(QColor(colors.GANTT_GRID), 1))
                g.drawLine(int(x), MARGEN_SUP, int(x), alto_zona)
                g.setPen(QColor(colors.TEXT_MUTED))
                g.drawText(QRectF(x - 30, alto_zona + 3, 60, 16), Qt.AlignCenter, ms(t))
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
            g.setBrush(QColor(s.color))
            g.drawRoundedRect(r, 3, 3)
            if r.width() > 18:
                p = self._buscar(s.pid)
                g.setPen(QColor(colors.TEXT_ON_ACCENT))
                g.drawText(r, Qt.AlignCenter, p.letra if p else "")
            if s is self._hover:
                g.setPen(QPen(QColor(colors.GANTT_HOVER), 2))
                g.setBrush(Qt.NoBrush)
                g.drawRoundedRect(r, 3, 3)

        # línea del "ahora"
        x = self._x(self.reloj, t0)
        g.setPen(QPen(QColor(colors.GANTT_NOW), 1, Qt.DashLine))
        g.drawLine(int(x), MARGEN_SUP, int(x), alto_zona)


class GanttView(Panel):
    def __init__(self, linea, buscar, parent=None):
        super().__init__("GANTT / RECORRIDO DE CPU", parent)
        self._lienzo = _Lienzo(linea, buscar)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setWidget(self._lienzo)
        self.cuerpo.addWidget(scroll, 1)

    def refrescar(self, reloj: int):
        self._lienzo.refrescar(reloj)
