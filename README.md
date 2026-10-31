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

## Guía de lectura y nombres del código

Para estudiar el proyecto, sigue este orden:

1. `estructuras/lista_enlazada.py`: `Nodo` guarda el dato y el enlace;
   `ListaEnlazada` permite agregar, eliminar y recorrer los procesos.
2. `simulacion/proceso.py`: datos de cada proceso y cálculo de sus porcentajes.
3. `simulacion/planificador.py`: cálculo del quantum y criterios de selección.
4. `simulacion/motor.py`: `paso()` coordina el avance del reloj y los movimientos
   entre preparados, CPU, suspendidos y terminados.
5. `aplicacion/controlador.py`: conecta los botones con el motor y publica
   eventos y cambios para que se actualice la pantalla.
6. `interfaz/ventana_principal.py`: crea la cabecera, el panel lateral y el panel
   de ejecución mediante funciones separadas.
7. `interfaz/componentes/`: `BarraControles`, `FormularioProceso`, `PanelColas`,
   `TarjetaProceso`, `PanelCpu`, `PanelBcp`, `ResumenSimulacion` e `HistorialCpu`.
   El historial dibuja por separado filas, eje, identificadores y segmentos.

Los nombres expresan qué representa cada dato: `proceso_candidato`,
`tiempo_transcurrido`, `divisor_quantum`, `barra_controles` o `indice_tarjeta`.
`cambiar_divisor_quantum()` modifica el divisor usado para calcular los turnos.
`formatear_milisegundos()` convierte un número en texto como `1.500 ms`.

Se mantienen las siglas propias del tema: PID (identificador de proceso),
CPU (procesador), BCP (bloque de control de proceso), E/S (entrada/salida) y
ms (milisegundos). `seed` es la semilla usada para repetir escenarios aleatorios.
En Qt, `parent` indica el componente padre; métodos como `paintEvent()` y
`mouseMoveEvent()` conservan sus nombres porque Qt los llama automáticamente.
`self` representa el objeto actual y `_` indica un dato que no necesitamos usar.
Los nombres de estilo como `Primary` identifican reglas del archivo QSS.

## Dónde cambiar cada cosa

| Quiero cambiar… | Archivo |
| --- | --- |
| Distribución de los paneles | `interfaz/ventana_principal.py` |
| Botones y opciones de reproducción | `interfaz/componentes/barra_controles.py` |
| Campos de creación | `interfaz/componentes/formulario_proceso.py` |
| Tarjetas y colas | `interfaz/componentes/tarjeta_proceso.py`, `panel_colas.py` |
| Información de CPU | `interfaz/componentes/panel_cpu.py` |
| Campos del BCP | `interfaz/componentes/bcp_campos.py` |
| Detalle BCP del proceso en CPU | `interfaz/componentes/panel_bcp.py` |
| Dibujo y ventana temporal del Gantt | `interfaz/componentes/grafico_gantt.py` |
| Indicadores superiores | `interfaz/componentes/resumen.py` |
| Colores | `interfaz/estilos/colores.py` |
| Estilos visuales y carga del tema | `interfaz/estilos/oscuro.qss`, `tema.py` |
| Textos de tiempo y tooltips | `interfaz/formato.py` |
| Acciones, selección y actualización de la ventana | `aplicacion/controlador.py` |
| Temporizador y velocidad base | `aplicacion/temporizador.py` |
| Lista simplemente enlazada y nodos | `estructuras/lista_enlazada.py` |
| Avance del tiempo, colas y transiciones | `simulacion/motor.py` |
| Selección del próximo proceso y cálculo del quantum | `simulacion/planificador.py` |
| Datos del proceso | `simulacion/proceso.py` |
| Estados posibles | `simulacion/estados.py` |
| Registro de intervalos de CPU | `simulacion/linea_tiempo.py` |
| Prioridades, rangos y paso simulado | `simulacion/configuracion.py` |
| Generación aleatoria | `simulacion/generador.py` |

## Estructura de datos: lista simplemente enlazada

La carpeta `estructuras/` contiene nuestra implementación independiente de Qt:

- `Nodo` guarda `dato` y un enlace `siguiente`. No tiene enlace al anterior.
- `ListaEnlazada` conserva referencias al primer y último nodo y la cantidad.
- `agregar(dato)` inserta al final en O(1).
- `eliminar(dato)` recorre los nodos y elimina la primera coincidencia en O(n).
  Si el dato no existe, lanza `ValueError`.
- `limpiar()` vacía la estructura. `len(lista)`, `if lista` y `for dato in lista`
  permiten consultar su tamaño, comprobar si tiene datos y recorrerla.

```text
primero → [Proceso A | siguiente] → [Proceso B | siguiente] → None
                                              ↑
                                            ultimo
```

`MotorSimulacion` usa `ListaEnlazada[Proceso]` para `preparados`, `suspendidos`
y `terminados`, reemplazando las listas de Python anteriores. Los nodos guardan
referencias a los mismos procesos; al cambiar de estado, el motor elimina el
proceso de una colección y lo agrega a la siguiente.

El planificador recorre los preparados para seleccionar por prioridad más alta,
quantum más grande y orden de llegada. Esta selección sigue siendo O(n).
`preparados_ordenados()` crea una lista temporal ordenada para mostrar las tarjetas;
no sustituye la lista enlazada que almacena los preparados en el motor.

Se conserva el diccionario `procesos` para buscar por PID, así como las listas de
mensajes y segmentos del historial, que cumplen funciones diferentes.
Al recorrer una lista enlazada se puede eliminar el dato que acaba de entregarse,
como al devolver procesos de E/S a preparados. No se deben eliminar otros nodos
ni agregar datos a esa misma colección durante el recorrido.

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

## Cómo leer y explicar el algoritmo PMA-QMG-P

Empieza por `simulacion/planificador.py`:

1. `calcular_quantum()` divide el tiempo total del proceso entre el divisor
   configurado y redondea a múltiplos del paso de simulación.
2. `clave_orden()` expresa las reglas: mayor prioridad, mayor quantum y llegada
   más antigua. Se compara cada criterio solo cuando empata el anterior.
3. `seleccionar_siguiente_proceso()` recorre los preparados de la lista enlazada
   y conserva el mejor candidato. No mueve procesos ni modifica sus estados.
4. `explicar_seleccion()` genera el motivo que se registra al entrar a CPU.

Ejemplo: A tiene prioridad 3 y quantum 200; B tiene prioridad 5 y quantum 100;
C tiene prioridad 5 y quantum 200. Gana C: supera a A por prioridad y a B por
quantum. Si otro proceso empata con C en ambos valores, gana el que llegó antes
a preparados. Cada regreso a preparados recibe un nuevo número de llegada.

Después lee `paso()` en `simulacion/motor.py`. El motor aplica la selección y
administra el tiempo y los cambios de estado:

1. Si la CPU está libre, asigna el siguiente proceso.
2. Calcula el tiempo hasta el evento más cercano, sin sobrepasar el fin del paso.
3. Actualiza el reloj, la ejecución, la espera y los bloqueos de E/S.
4. Devuelve a preparados los procesos cuya E/S acaba de finalizar.
5. Comprueba si el proceso en CPU terminó, pidió E/S o agotó su quantum, en ese
   orden. Si nada de eso ocurre, continúa ejecutándose.
6. Si quedó libre la CPU, selecciona otro proceso y aprovecha el tiempo sobrante.

Los métodos de movimientos entre estados están al final de `motor.py`, con
nombres como `_asignar_cpu_al_siguiente_proceso()` y
`_devolver_por_quantum_agotado()`. La llegada de un proceso más prioritario no
interrumpe al proceso actual: la selección ocurre cuando la CPU queda libre.

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
