from enum import Enum


class Estado(Enum):
    PREPARADO = "Preparado"
    EJECUCION = "Ejecución"
    SUSPENDIDO = "Suspendido"
    TERMINADO = "Terminado"
