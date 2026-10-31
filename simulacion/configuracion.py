"""Parámetros de la simulación. Cambia los valores aquí, no en la lógica."""

TICK_MS = 10                 # ms simulados que avanza cada tick

PID_INICIAL = 101
PRIORIDAD_MIN = 1
PRIORIDAD_MAX = 5

DIVISORES_QUANTUM = [2, 3, 4, 5, 8, 10]   # opciones del combo "Rata de quantum"
DIVISOR_QUANTUM_POR_DEFECTO = 5                   # Quantum = tiempo total / rata

TIEMPO_TOTAL_RANGO = (500, 3000)       # ms, al generar un proceso sin tiempo
INTERACTIVIDAD_RANGO = (0, 100)        # % de probabilidad de pedir E/S en cada turno
BLOQUEO_DURACION_RANGO = (100, 400)    # ms que dura un bloqueo

CAUSAS_BLOQUEO = [
    "Entrada/Salida de disco",
    "Espera de entrada del usuario",
    "Operación de red",
]

