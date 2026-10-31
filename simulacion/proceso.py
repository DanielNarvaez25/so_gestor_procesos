from dataclasses import dataclass
from .estados import Estado


@dataclass
class Proceso:
    pid: int
    nombre: str
    prioridad: int
    tiempo_total: int            
    quantum: int                 
    interactividad: int = 0      
    estado: Estado = Estado.PREPARADO

    orden_cola: int = 0          
    tiempo_ejecutado: int = 0
    quantum_usado: int = 0
    tiempo_espera: int = 0       

    causa_bloqueo: str = ""
    bloqueo_total: int = 0
    bloqueo_restante: int = 0
    bloqueo_en: int | None = None   

    @property
    def letra(self) -> str:
        partes = self.nombre.strip().split()
        return (partes[0][0] if partes else "?").upper()

    @property
    def tiempo_restante(self) -> int:
        return max(0, self.tiempo_total - self.tiempo_ejecutado)

    @property
    def progreso_quantum(self) -> int:
        if self.quantum == 0:
            return 0
        porcentaje_usado = round(100 * self.quantum_usado / self.quantum)
        return min(100, porcentaje_usado)

    @property
    def progreso_total(self) -> int:
        if self.tiempo_total == 0:
            return 0
        porcentaje_ejecutado = round(100 * self.tiempo_ejecutado / self.tiempo_total)
        return min(100, porcentaje_ejecutado)

    @property
    def tiempo_en_bloqueo(self) -> int:
        return self.bloqueo_total - self.bloqueo_restante
