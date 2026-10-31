"""Etiqueta de una línea que conserva el texto completo en el tooltip."""
from PySide6.QtCore import QSize, Qt
from PySide6.QtWidgets import QLabel, QSizePolicy


class EtiquetaElidida(QLabel):
    def __init__(self, text="", parent=None):
        super().__init__(parent)
        self._texto_completo = text
        self.setTextFormat(Qt.PlainText)
        self.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Preferred)
        self.setMinimumWidth(0)
        self.setText(text)

    def setText(self, text):
        self._texto_completo = text
        self.setToolTip(text)
        self._actualizar_texto_visible()

    def _actualizar_texto_visible(self):
        super().setText(self.fontMetrics().elidedText(self._texto_completo, Qt.ElideRight, max(1, self.contentsRect().width())))

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._actualizar_texto_visible()

    def minimumSizeHint(self):
        return QSize(0, super().minimumSizeHint().height())
