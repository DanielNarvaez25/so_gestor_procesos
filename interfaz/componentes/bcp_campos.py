"""Campos del BCP del proceso en CPU. Edita EJECUCION para cambiar lo mostrado."""
from dataclasses import dataclass
from typing import Callable

from interfaz.estilos import colores
from interfaz.formato import formatear_milisegundos


@dataclass
class Campo:
    etiqueta: str
    valor: Callable[[object], str]                   # Proceso -> texto
    color: Callable[[object], str] | None = None     # Proceso -> color del texto (opcional)


PID = Campo("PID", lambda proceso: str(proceso.pid))
NOMBRE = Campo("Nombre", lambda proceso: proceso.nombre)
ESTADO = Campo("Estado", lambda proceso: proceso.estado.value, lambda proceso: colores.color_estado(proceso.estado))
PRIORIDAD = Campo("Prioridad", lambda proceso: str(proceso.prioridad))
QUANTUM = Campo("Quantum", lambda proceso: formatear_milisegundos(proceso.quantum))
T_TOTAL = Campo("Tiempo total", lambda proceso: formatear_milisegundos(proceso.tiempo_total))
T_EJECUTADO = Campo("Tiempo ejecutado", lambda proceso: formatear_milisegundos(proceso.tiempo_ejecutado))


# Campos del panel BCP en CPU
EJECUCION = [PID, NOMBRE, ESTADO, PRIORIDAD, QUANTUM, T_TOTAL, T_EJECUTADO]
