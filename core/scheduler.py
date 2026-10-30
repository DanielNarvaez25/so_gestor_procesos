"""Algoritmo PMA-QMG-P: Prioridad Más Alta -> Quantum Más Grande -> Primero."""
from .config import TICK_MS


def calcular_quantum(tiempo_total: int, rata: int) -> int:
    """Quantum = tiempo total / rata, redondeado a múltiplo del tick."""
    q = round(tiempo_total / max(1, rata) / TICK_MS) * TICK_MS
    return max(TICK_MS, q)


def clave_orden(p) -> tuple:
    """Menor clave = se elige primero."""
    return (-p.prioridad, -p.quantum, p.orden_cola)


def elegir(preparados):
    return min(preparados, key=clave_orden, default=None)


def explicar(elegido, preparados) -> list[str]:
    """Razones por las que `elegido` ganó (para el panel '¿Por qué?')."""
    otros = [p for p in preparados if p is not elegido]
    if not otros:
        return ["Era el único proceso preparado."]
    razones = [f"Prioridad más alta ({elegido.prioridad})."]
    empate_prio = [p for p in otros if p.prioridad == elegido.prioridad]
    if empate_prio:
        razones = [f"Empate en prioridad ({elegido.prioridad})."]
        empate_q = [p for p in empate_prio if p.quantum == elegido.quantum]
        if empate_q:
            razones.append(f"Empate en quantum ({elegido.quantum} ms): llegó primero a la cola.")
        else:
            razones.append(f"Quantum más grande ({elegido.quantum} ms).")
    return razones
