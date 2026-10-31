"""Datos aleatorios para el botón 'Generar aleatorio'."""
import random

from simulacion import configuracion


def datos_aleatorios(generador_aleatorio: random.Random | None = None) -> dict:
    generador_aleatorio = generador_aleatorio or random
    paso_simulacion = configuracion.TICK_MS
    return {
        "prioridad": generador_aleatorio.randint(configuracion.PRIORIDAD_MIN, configuracion.PRIORIDAD_MAX),
        "tiempo_total": generador_aleatorio.randrange(configuracion.TIEMPO_TOTAL_RANGO[0], configuracion.TIEMPO_TOTAL_RANGO[1] + 1, paso_simulacion),
        "interactividad": generador_aleatorio.randint(*configuracion.INTERACTIVIDAD_RANGO),
    }
