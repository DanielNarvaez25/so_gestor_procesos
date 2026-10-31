# Simulador de procesos

Simulador PMA-QMG-P con interfaz PySide6. Se ejecuta con:

```sh
pip install -r requirements.txt
python main.py
```

## Arquitectura y recorrido de una acción

La aplicación tiene tres partes: `simulacion` contiene las reglas, `aplicacion`
coordina las acciones y `interfaz` muestra los resultados. `main.py` crea y conecta
el motor, el controlador y la ventana.

```text
Botón Paso → ControladorSimulacion.paso() → MotorSimulacion.paso()
           → publicación de mensajes y cambios → VentanaPrincipal.mostrar()
```

El temporizador llama a la misma acción que el botón Paso. Su intervalo controla
la velocidad de reproducción; el motor controla exclusivamente el tiempo virtual.

## Dónde cambiar cada cosa

| Quiero cambiar… | Archivo |
| --- | --- |
| Distribución de los paneles | `interfaz/ventana_principal.py` |
| Botones y opciones de reproducción | `interfaz/componentes/barra_controles.py` |
| Campos de creación | `interfaz/componentes/formulario_proceso.py` |
| Tarjetas y colas | `interfaz/componentes/tarjeta_proceso.py`, `panel_colas.py` |
| Información de CPU | `interfaz/componentes/panel_cpu.py` |
| Campos del BCP | `interfaz/componentes/bcp_campos.py` |
| Tablas y detalle BCP | `interfaz/componentes/tabla_bcp.py`, `panel_bcp.py` |
| Dibujo y ventana temporal del Gantt | `interfaz/componentes/grafico_gantt.py` |
| Indicadores superiores | `interfaz/componentes/resumen.py` |
| Colores | `interfaz/estilos/colores.py` |
| Estilos visuales y carga del tema | `interfaz/estilos/oscuro.qss`, `tema.py` |
| Textos de tiempo y tooltips | `interfaz/formato.py` |
| Acciones, selección y actualización de la ventana | `aplicacion/controlador.py` |
| Temporizador y velocidad base | `aplicacion/temporizador.py` |
| Avance del tiempo, colas y transiciones | `simulacion/motor.py` |
| Selección del próximo proceso y cálculo del quantum | `simulacion/planificador.py` |
| Datos del proceso | `simulacion/proceso.py` |
| Estados posibles | `simulacion/estados.py` |
| Registro de intervalos de CPU | `simulacion/linea_tiempo.py` |
| Prioridades, rangos y paso simulado | `simulacion/configuracion.py` |
| Generación aleatoria | `simulacion/generador.py` |

## Reglas para mantener la separación

- El motor no importa Qt, colores ni componentes de interfaz.
- El controlador recibe las acciones y es dueño del temporizador y la selección.
- La ventana construye los paneles y representa los datos recibidos.
- Los componentes visuales emiten acciones; no modifican procesos ni colas.
- Las mutaciones de la simulación pasan por el motor. Los datos que recibe la
  vista son referencias de lectura por convención, no copias inmutables.
- El planificador concentra las reglas de selección y orden de preparados.
- Los mensajes se acumulan en el motor y el controlador los publica después de
  cada operación, cuando el estado ya es consistente. En ejecuciones largas sin
  interfaz, consumir `extraer_eventos()` periódicamente evita acumular mensajes.

No hay una clase por cada operación: las transiciones permanecen juntas en el
motor para poder seguir el ciclo completo de un proceso.

## Simular sin interfaz

```python
from simulacion.motor import MotorSimulacion

motor = MotorSimulacion(seed=7)
motor.agregar_proceso(nombre="A", prioridad=3, tiempo_total=15, interactividad=0)
while motor.hay_trabajo:
    motor.paso()
    for mensaje in motor.extraer_eventos():
        print(mensaje)
assert motor.reloj == 15
```

La generación aleatoria del formulario utiliza ahora la misma fuente con semilla
que el motor. La misma semilla y secuencia de acciones reproducen el escenario.
Reiniciar limpia los procesos y el reloj, conserva rata y velocidad y continúa
la secuencia aleatoria; no vuelve a sembrar el generador.

## Reglas temporales conservadas

- Selección por prioridad más alta, quantum más grande y llegada a la cola.
- Un nuevo proceso con mayor prioridad no interrumpe el turno actual.
- Cada paso avanza hasta 10 ms y resuelve eventos en su instante exacto.
- El tiempo restante del paso puede usarse para el siguiente proceso.
- Al finalizar todos los procesos, la reproducción se detiene.
- Cambiar la rata actualiza preparados y suspendidos; el proceso en CPU conserva
  el quantum y la E/S programados hasta terminar su turno.

## Pruebas

```sh
python -m unittest discover -s tests -v
```

`test_motor.py` verifica tiempos, planificación, E/S e invariantes;
`test_controlador.py` verifica reproducción, mensajes y reinicio;
`test_interfaz.py` verifica controles, selección y dibujo sin pantalla;
`test_independencia_motor.py` comprueba que el motor se ejecuta sin importar Qt
 y que la generación con semilla es reproducible.

Para ejecutar solamente las regresiones del motor sin Qt:

```sh
python -m unittest discover -s tests -p test_motor.py -v
```

## Equivalencias con la estructura anterior

- `core/` → `simulacion/`; la parte Qt de `Simulation` está en `aplicacion/`.
- `ui/main_window.py` → `interfaz/ventana_principal.py`.
- `ui/widgets/` → `interfaz/componentes/`.
- `utils/colors.py`, `utils/theme.py`, `resources/styles/dark.qss` → `interfaz/estilos/`.
- `utils/formato.py` → `interfaz/formato.py`.
- `utils/random_generator.py` → `simulacion/generador.py`.

Las importaciones internas cambiaron; los programas externos que importaban
`core` o `ui` deben utilizar las nuevas rutas. El arranque sigue siendo `python main.py`.

## Explorar el recorrido de CPU

El Gantt conserva el historial desde 0 ms. Arrastra su barra horizontal para
consultar eventos anteriores; al hacerlo se desactiva **Seguir ejecución**.
**Inicio** vuelve al primer evento y **Ahora** retoma el seguimiento del final.
El zoom de 50 % a 400 % permite ajustar el detalle. Los tooltips siguen mostrando
la información de cada segmento. Reiniciar limpia el historial y vuelve al origen.
En ventanas bajas, la página completa permite desplazamiento vertical para
mantener accesibles los paneles sin comprimir sus controles.
