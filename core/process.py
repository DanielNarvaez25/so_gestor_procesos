"""Proceso = BCP (bloque de control de proceso). Sin dependencias de Qt."""
from dataclasses import dataclass

from .states import Estado


@dataclass
class Proceso:
    pid: int
    nombre: str
    prioridad: int
    tiempo_total: int            # ms de CPU que necesita en total
    quantum: int                 # ms por turno
    color: str
    interactividad: int = 0      # % de probabilidad de pedir E/S en cada turno
    estado: Estado = Estado.PREPARADO

    orden_cola: int = 0          # turno de entrada a Preparados (desempate "primero")
    tiempo_ejecutado: int = 0
    quantum_usado: int = 0
    tiempo_espera: int = 0       # acumulado en Preparados

    causa_bloqueo: str = ""
    bloqueo_total: int = 0
    bloqueo_restante: int = 0
    bloqueo_en: int | None = None   # ms de quantum tras los que pedirá E/S (este turno)

    @property
    def letra(self) -> str:
        partes = self.nombre.strip().split()
        return (partes[-1][0] if partes else "?").upper()

    @property
    def tiempo_restante(self) -> int:
        return max(0, self.tiempo_total - self.tiempo_ejecutado)

    @property
    def progreso_quantum(self) -> int:
        return min(100, round(100 * self.quantum_usado / self.quantum)) if self.quantum else 0

    @property
    def progreso_total(self) -> int:
        return min(100, round(100 * self.tiempo_ejecutado / self.tiempo_total)) if self.tiempo_total else 0

    @property
    def tiempo_en_bloqueo(self) -> int:
        return self.bloqueo_total - self.bloqueo_restante
