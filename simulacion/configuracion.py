"""Parámetros de la simulación."""

TICK_MS = 10                 

PID_INICIAL = 101
PRIORIDAD_MIN = 1
PRIORIDAD_MAX = 5

DIVISORES_QUANTUM = [2, 3, 4, 5, 8, 10]   
DIVISOR_QUANTUM_POR_DEFECTO = 5                  

TIEMPO_TOTAL_RANGO = (500, 3000)       
INTERACTIVIDAD_RANGO = (0, 100)        
BLOQUEO_DURACION_RANGO = (100, 400)  

CAUSAS_BLOQUEO = [
    "Entrada/Salida de disco",
    "Espera de entrada del usuario",
    "Operación de red",
]

