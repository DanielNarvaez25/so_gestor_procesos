"""Segmentos de la línea de tiempo (Gantt)."""
from dataclasses import dataclass


@dataclass
class Segmento:
    pid: int
    nombre: str
    color: str
    prioridad: int
    inicio: int
    fin: int

    @property
    def duracion(self) -> int:
        return self.fin - self.inicio


class LineaTiempo:
    def __init__(self):
        self.segmentos: list[Segmento] = []
        self._abierto: Segmento | None = None

    @property
    def abierto(self) -> Segmento | None:
        return self._abierto

    def abrir(self, proceso, t: int) -> Segmento:
        self._abierto = Segmento(proceso.pid, proceso.nombre, proceso.color, proceso.prioridad, t, t)
        self.segmentos.append(self._abierto)
        return self._abierto

    def extender(self, t: int) -> Segmento | None:
        if self._abierto:
            self._abierto.fin = t
        return self._abierto

    def cerrar(self) -> None:
        self._abierto = None

    def limpiar(self) -> None:
        self.segmentos.clear()
        self._abierto = None
