"""Carga el QSS reemplazando {{VARIABLE}} por el valor definido en interfaz/estilos/colores.py."""
import re
from pathlib import Path

from PySide6.QtCore import QEvent, QObject
from PySide6.QtWidgets import QPushButton

from interfaz.estilos import colores

RUTA_QSS = Path(__file__).with_name("oscuro.qss")


def _variables() -> dict[str, str]:
    variables_colores = {}
    for nombre, valor in vars(colores).items():
        if nombre.isupper() and isinstance(valor, str):
            variables_colores[nombre] = valor
    return variables_colores


def cargar_qss(ruta: Path = RUTA_QSS) -> str:
    variables = _variables()

    def reemplazo(coincidencia: re.Match) -> str:
        nombre = coincidencia.group(1)
        if nombre not in variables:
            raise KeyError(f"El color '{nombre}' no existe en interfaz/estilos/colores.py")
        return variables[nombre]

    return re.sub(r"\{\{(\w+)\}\}", reemplazo, Path(ruta).read_text(encoding="utf-8"))


class _EfectoCursorBotones(QObject):
    """Qt no aplica :hover a botones desactivados; conserva el estado visual."""

    def eventFilter(self, objeto, evento):
        if isinstance(objeto, QPushButton) and evento.type() in (QEvent.Enter, QEvent.Leave):
            objeto.setProperty("cursorEncima", evento.type() == QEvent.Enter)
            objeto.style().unpolish(objeto)
            objeto.style().polish(objeto)
            objeto.update()
        return False


def aplicar_tema(aplicacion, ruta: Path = RUTA_QSS) -> None:
    aplicacion.setStyleSheet(cargar_qss(ruta))
    if not hasattr(aplicacion, "_efecto_cursor_botones"):
        aplicacion._efecto_cursor_botones = _EfectoCursorBotones(aplicacion)
        aplicacion.installEventFilter(aplicacion._efecto_cursor_botones)
