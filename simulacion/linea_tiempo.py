"""Segmentos de la línea de tiempo (Gantt)."""
from dataclasses import dataclass


@dataclass
class Segmento:
    pid: int
    nombre: str
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

    def abrir(self, proceso, instante: int) -> Segmento:
        self._abierto = Segmento(proceso.pid, proceso.nombre, proceso.prioridad, instante, instante)
        self.segmentos.append(self._abierto)
        return self._abierto

    def extender(self, instante: int) -> Segmento | None:
        if self._abierto:
            self._abierto.fin = instante
        return self._abierto

    def cerrar(self) -> None:
        self._abierto = None

    def limpiar(self) -> None:
        self.segmentos.clear()
        self._abierto = None
