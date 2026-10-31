"""Qué campos del BCP se muestran en cada panel/tabla. Para agregar o quitar un dato,
edita las listas de abajo; los widgets no cambian."""
from dataclasses import dataclass
from typing import Callable

from interfaz.estilos import colores as colors
from interfaz.formato import ms


@dataclass
class Campo:
    etiqueta: str
    valor: Callable[[object], str]                   # Proceso -> texto
    color: Callable[[object], str] | None = None     # Proceso -> color del texto (opcional)


PID = Campo("PID", lambda p: str(p.pid))
NOMBRE = Campo("Nombre", lambda p: p.nombre)
ESTADO = Campo("Estado", lambda p: p.estado.value, lambda p: colors.color_estado(p.estado))
PRIORIDAD = Campo("Prioridad", lambda p: str(p.prioridad))
QUANTUM = Campo("Quantum", lambda p: ms(p.quantum))
INTERACTIVIDAD = Campo("Interactividad", lambda p: f"{p.interactividad}%")
T_TOTAL = Campo("Tiempo total", lambda p: ms(p.tiempo_total))
T_EJECUTADO = Campo("Tiempo ejecutado", lambda p: ms(p.tiempo_ejecutado))
T_EJECUCION = Campo("Tiempo de ejecución", lambda p: f"{ms(p.tiempo_ejecutado)} / {ms(p.tiempo_total)}")
CAUSA = Campo("Causa de bloqueo", lambda p: p.causa_bloqueo if p.estado.name == "SUSPENDIDO" else "—")
T_ESPERA = Campo("Avance E/S", lambda p: f"{ms(p.tiempo_en_bloqueo)} / {ms(p.bloqueo_total)}" if p.estado.name == "SUSPENDIDO" else "—")

ESPERA_CPU = Campo("Espera en cola", lambda p: ms(p.tiempo_espera))
RESTANTE = Campo("CPU restante", lambda p: ms(p.tiempo_restante))

# Paneles de detalle
EJECUCION = [PID, NOMBRE, ESTADO, PRIORIDAD, QUANTUM, T_TOTAL, T_EJECUTADO]
SELECCIONADO = [PID, NOMBRE, ESTADO, PRIORIDAD, QUANTUM, INTERACTIVIDAD, T_TOTAL, T_EJECUTADO, RESTANTE, ESPERA_CPU, CAUSA, T_ESPERA]

# Columnas de las tablas inferiores
TABLA_PREPARADOS = [PID, NOMBRE, ESTADO, PRIORIDAD, QUANTUM, T_EJECUCION]
TABLA_SUSPENDIDOS = [PID, NOMBRE, ESTADO, CAUSA, T_ESPERA, T_EJECUCION]
