"""Datos aleatorios para el botón 'Generar aleatorio'."""
import random

from simulacion import configuracion as config


def datos_aleatorios(rng: random.Random | None = None) -> dict:
    rng = rng or random
    t = config.TICK_MS
    return {
        "prioridad": rng.randint(config.PRIORIDAD_MIN, config.PRIORIDAD_MAX),
        "tiempo_total": rng.randrange(config.TIEMPO_TOTAL_RANGO[0], config.TIEMPO_TOTAL_RANGO[1] + 1, t),
        "interactividad": rng.randint(*config.INTERACTIVIDAD_RANGO),
    }
