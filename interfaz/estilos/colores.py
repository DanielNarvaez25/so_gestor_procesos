"""Paleta central de la interfaz, el QSS y el Gantt."""
BG_APP = "#090e1c"
BG_PANEL = "#141e33"
BG_PANEL_ALT = "#1b2942"
BG_INPUT = "#0d1629"
BG_HOVER = "#263c59"
BORDER = "#304361"
TEXT = "#edf4ff"
TEXT_MUTED = "#a7b8d3"
TEXT_ON_ACCENT = "#081a20"
ACCENT = "#55e6c1"
ACCENT_HOVER = "#92f5da"
DANGER = "#ff7b89"
STATE_PREPARADO = "#79b8ff"
STATE_EJECUCION = "#55e6c1"
STATE_SUSPENDIDO = "#f4c779"
STATE_TERMINADO = "#b2a2f7"
GANTT_BG = "#0d1629"
GANTT_GRID = "#243344"
GANTT_NOW = "#55e6c1"
GANTT_HOVER = "#edf4ff"
TOOLTIP_BG = "#263c59"
TOOLTIP_TEXT = "#edf4ff"
PALETA_PROCESOS = ["#79b8ff", "#55e6c1", "#f4c779", "#b2a2f7", "#ff93ab", "#6dd5ed", "#ffa579"]
COLOR_ESTADO = {
    "PREPARADO": STATE_PREPARADO, "EJECUCION": STATE_EJECUCION,
    "SUSPENDIDO": STATE_SUSPENDIDO, "TERMINADO": STATE_TERMINADO,
}

def color_proceso(indice: int) -> str:
    return PALETA_PROCESOS[indice % len(PALETA_PROCESOS)]

def color_estado(estado) -> str:
    return COLOR_ESTADO[estado.name]


def color_pid(pid: int) -> str:
    from simulacion.configuracion import PID_INICIAL
    return color_proceso(pid - PID_INICIAL)

HERO_START = "#203c60"
HERO_END = "#172338"
