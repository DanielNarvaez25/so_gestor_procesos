"""Algoritmo PMA-QMG-P: Prioridad Más Alta -> Quantum Más Grande -> Primero."""
from collections.abc import Iterable

from .configuracion import TICK_MS
from .proceso import Proceso


def calcular_quantum(tiempo_total: int, divisor_quantum: int) -> int:
    """Divide el tiempo total y redondea a múltiplos de 10 ms, como mínimo 10 ms."""
    quantum_sin_redondear = tiempo_total / max(1, divisor_quantum)
    cantidad_pasos = round(quantum_sin_redondear / TICK_MS)
    quantum_redondeado = cantidad_pasos * TICK_MS
    return max(TICK_MS, quantum_redondeado)


def clave_orden(proceso: Proceso) -> tuple[int, int, int]:
    """Las tres reglas del algoritmo, en orden de importancia.

    Python compara tuplas de izquierda a derecha y elige la menor.
    Los signos negativos hacen que una prioridad o quantum mayor gane.
    El orden de llegada es positivo: gana quien tenga el número menor.
    """
    prioridad_mayor_primero = -proceso.prioridad
    quantum_mayor_primero = -proceso.quantum
    llegada_mas_antigua_primero = proceso.orden_cola
    return (prioridad_mayor_primero, quantum_mayor_primero, llegada_mas_antigua_primero)


def seleccionar_siguiente_proceso(preparados: Iterable[Proceso]) -> Proceso | None:
    """Recorre la lista enlazada y conserva el proceso con mejor preferencia.

    No elimina nodos ni cambia estados: el motor se encarga de esas acciones.
    Si la colección está vacía, devuelve None. El recorrido cuesta O(n).
    """
    proceso_elegido = None
    for proceso_candidato in preparados:
        if proceso_elegido is None:
            proceso_elegido = proceso_candidato
        elif clave_orden(proceso_candidato) < clave_orden(proceso_elegido):
            proceso_elegido = proceso_candidato
    return proceso_elegido


def explicar_seleccion(elegido: Proceso, preparados: Iterable[Proceso]) -> list[str]:
    """Describe la regla que decidió la selección para el registro de eventos."""
    otros_procesos = [proceso for proceso in preparados if proceso is not elegido]
    if not otros_procesos:
        return ["Era el único proceso preparado."]
    razones = [f"Prioridad más alta ({elegido.prioridad})."]
    procesos_con_igual_prioridad = [proceso for proceso in otros_procesos if proceso.prioridad == elegido.prioridad]
    if procesos_con_igual_prioridad:
        razones = [f"Empate en prioridad ({elegido.prioridad})."]
        procesos_con_igual_quantum = [proceso for proceso in procesos_con_igual_prioridad if proceso.quantum == elegido.quantum]
        if procesos_con_igual_quantum:
            razones.append(f"Empate en quantum ({elegido.quantum} ms): llegó primero a la cola.")
        else:
            razones.append(f"Quantum más grande ({elegido.quantum} ms).")
    return razones
