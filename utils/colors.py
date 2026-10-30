"""Paleta central de la interfaz, el QSS y el Gantt."""
BG_APP = "#0b1017"
BG_PANEL = "#121b26"
BG_PANEL_ALT = "#172331"
BG_INPUT = "#0e1721"
BG_HOVER = "#203447"
BORDER = "#2a394a"
TEXT = "#eaf2f8"
TEXT_MUTED = "#9bafc3"
TEXT_ON_ACCENT = "#081a20"
ACCENT = "#57dfc5"
ACCENT_HOVER = "#86efda"
DANGER = "#ff7b89"
STATE_PREPARADO = "#79b8ff"
STATE_EJECUCION = "#57dfc5"
STATE_SUSPENDIDO = "#f4c779"
STATE_TERMINADO = "#b2a2f7"
GANTT_BG = "#0e1721"
GANTT_GRID = "#243344"
GANTT_NOW = "#57dfc5"
GANTT_HOVER = "#eaf2f8"
TOOLTIP_BG = "#203447"
TOOLTIP_TEXT = "#eaf2f8"
PALETA_PROCESOS = ["#79b8ff", "#57dfc5", "#f4c779", "#b2a2f7", "#ff93ab", "#6dd5ed", "#ffa579"]
COLOR_ESTADO = {
    "PREPARADO": STATE_PREPARADO, "EJECUCION": STATE_EJECUCION,
    "SUSPENDIDO": STATE_SUSPENDIDO, "TERMINADO": STATE_TERMINADO,
}

def color_proceso(indice: int) -> str:
    return PALETA_PROCESOS[indice % len(PALETA_PROCESOS)]

def color_estado(estado) -> str:
    return COLOR_ESTADO[estado.name]
