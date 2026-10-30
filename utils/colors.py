"""
PALETA CENTRAL DE COLORES
-------------------------
Todo color de la aplicación sale de este archivo.
- En el QSS se usa como {{NOMBRE}} (ver resources/styles/dark.qss).
- En código Python (por ejemplo el Gantt): QColor(colors.NOMBRE).

Para cambiar el aspecto basta con editar los valores de aquí.
Para agregar un color nuevo: defínelo en MAYÚSCULAS y úsalo; nada más que tocar.
"""

# ---------- Fondos ----------
BG_APP = "#0d1526"
BG_PANEL = "#131d33"
BG_PANEL_ALT = "#0f1930"
BG_INPUT = "#0f1930"
BG_HOVER = "#1a2745"
BORDER = "#22304f"

# ---------- Texto ----------
TEXT = "#e9eef8"
TEXT_MUTED = "#8697bd"
TEXT_ON_ACCENT = "#08111f"

# ---------- Acentos y botones ----------
ACCENT = "#3d8bff"
ACCENT_HOVER = "#5a9dff"
DANGER = "#e34a5f"

# ---------- Estados de proceso ----------
STATE_PREPARADO = "#3d8bff"
STATE_EJECUCION = "#2ecc82"
STATE_SUSPENDIDO = "#ffb238"
STATE_TERMINADO = "#8697bd"

# ---------- Línea de tiempo (Gantt) ----------
GANTT_BG = "#0a1120"
GANTT_GRID = "#22304f"
GANTT_NOW = "#ffffff"
GANTT_HOVER = "#ffffff"      # borde de la barra bajo el mouse

# ---------- Tooltip (info al pasar el mouse sobre las barras) ----------
TOOLTIP_BG = "#0a1120"
TOOLTIP_TEXT = "#e9eef8"

# ---------- Colores de los procesos (se asignan en orden y se repiten) ----------
PALETA_PROCESOS = [
    "#ff5c8a",
    "#3d8bff",
    "#2ecc82",
    "#ffb238",
    "#b07dff",
    "#37c8e0",
    "#f2836b",
]

# Estado -> color. Las llaves son el NOMBRE del enum Estado.
COLOR_ESTADO = {
    "PREPARADO": STATE_PREPARADO,
    "EJECUCION": STATE_EJECUCION,
    "SUSPENDIDO": STATE_SUSPENDIDO,
    "TERMINADO": STATE_TERMINADO,
}


def color_proceso(indice: int) -> str:
    """Color fijo para el proceso número `indice` (0, 1, 2...)."""
    return PALETA_PROCESOS[indice % len(PALETA_PROCESOS)]


def color_estado(estado) -> str:
    """Color asociado a un Estado (usa estado.name)."""
    return COLOR_ESTADO[estado.name]
