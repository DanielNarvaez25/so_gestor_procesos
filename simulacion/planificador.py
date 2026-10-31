"""Algoritmo PMA-QMG-P: Prioridad Más Alta -> Quantum Más Grande -> Primero."""

from .configuracion import TICK_MS


def calcular_quantum(tiempo_total, divisor_quantum):
    """Divide el tiempo total y redondea a múltiplos de 10 ms, como mínimo 10 ms."""
    if divisor_quantum < 1:
        divisor_quantum = 1
    quantum_sin_redondear = tiempo_total / divisor_quantum
    cantidad_pasos = round(quantum_sin_redondear / TICK_MS)
    quantum_redondeado = cantidad_pasos * TICK_MS
    if quantum_redondeado < TICK_MS:
        return TICK_MS
    return quantum_redondeado


def tiene_preferencia(proceso_candidato, proceso_actual):
    """Compara dos procesos aplicando PMA, después QMG y finalmente llegada."""
    # 1. Prioridad más alta. 
    if proceso_candidato.prioridad > proceso_actual.prioridad:
        return True
    elif proceso_candidato.prioridad < proceso_actual.prioridad:
        return False
    else:
        # 2. Quantum más grande.
        if proceso_candidato.quantum > proceso_actual.quantum:
            return True
        elif proceso_candidato.quantum < proceso_actual.quantum:
            return False
        else:
            # 3. Desempate por PID
            if proceso_candidato.pid < proceso_actual.pid:
                return True
            else:
                return False


def seleccionar_siguiente_proceso(preparados):
    """Recorre la lista enlazada y conserva el proceso con mejor preferencia.
    """
    proceso_elegido = None
    for proceso_candidato in preparados:
        if proceso_elegido is None:
            proceso_elegido = proceso_candidato
        else:
            candidato_tiene_preferencia = tiene_preferencia(
                proceso_candidato, proceso_elegido
            )
            if candidato_tiene_preferencia:
                proceso_elegido = proceso_candidato
    return proceso_elegido


def ordenar_preparados(preparados):
    procesos_ordenados = []
    for proceso_candidato in preparados:
        posicion_insercion = 0
        while posicion_insercion < len(procesos_ordenados):
            proceso_en_posicion = procesos_ordenados[posicion_insercion]
            candidato_va_antes = tiene_preferencia(
                proceso_candidato, proceso_en_posicion
            )
            if candidato_va_antes:
                break
            posicion_insercion += 1
        procesos_ordenados.insert(posicion_insercion, proceso_candidato)
    return procesos_ordenados
