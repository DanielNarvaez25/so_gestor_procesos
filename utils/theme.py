"""Carga el QSS reemplazando {{VARIABLE}} por el valor definido en utils/colors.py."""
import re
from pathlib import Path

from . import colors

RUTA_QSS = Path(__file__).resolve().parent.parent / "resources" / "styles" / "dark.qss"


def _variables() -> dict[str, str]:
    return {n: v for n, v in vars(colors).items() if n.isupper() and isinstance(v, str)}


def cargar_qss(ruta: Path = RUTA_QSS) -> str:
    variables = _variables()

    def reemplazo(m: re.Match) -> str:
        nombre = m.group(1)
        if nombre not in variables:
            raise KeyError(f"El color '{nombre}' no existe en utils/colors.py")
        return variables[nombre]

    return re.sub(r"\{\{(\w+)\}\}", reemplazo, Path(ruta).read_text(encoding="utf-8"))


def aplicar_tema(app, ruta: Path = RUTA_QSS) -> None:
    app.setStyleSheet(cargar_qss(ruta))
