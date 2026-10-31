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

`MotorSimulacion` usa objetos `ListaEnlazada` para `preparados`, `suspendidos`
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

### Qué guarda cada colección

| Nombre en el motor | Estructura | Contenido |
| --- | --- | --- |
| `preparados` | Lista simplemente enlazada | Procesos esperando un turno de CPU. |
| `suspendidos` | Lista simplemente enlazada | Procesos esperando que finalice su E/S. |
| `terminados` | Lista simplemente enlazada | Procesos que ya ejecutaron todo su tiempo de CPU. |
| `procesos` | Diccionario por PID | Referencia a todos los procesos creados, para buscarlos. |
| `en_cpu` | Un objeto `Proceso` o `None` | El proceso que está ejecutándose; `None` indica CPU libre. |
| `eventos` | Lista de textos | Mensajes pendientes de entregar al controlador. |
| `linea.segmentos` | Lista de segmentos | Intervalos que se dibujan en el historial de CPU. |

El proceso y su nodo son cosas diferentes. El proceso contiene sus datos; el nodo
permite enlazarlo con el siguiente. Al mover un proceso a otra colección, se retira
su nodo de origen y se crea otro nodo que guarda la referencia al mismo proceso.
Su PID y su tiempo ejecutado se conservan.

### Cómo funcionan los enlaces

- `_primero` señala el nodo desde el que comienza el recorrido.
- `_ultimo` permite agregar al final sin recorrer todos los nodos.
- `_cantidad` guarda cuántos nodos hay; por eso `len(lista)` no necesita recorrerlos.
- `siguiente` es la referencia al próximo nodo. En el último nodo vale `None`.

Para agregar B a una lista que contiene A, se crea el nodo de B, se hace que
`A.siguiente` lo señale y se actualiza `_ultimo`. Para eliminar B de `A → B → C`,
se cambia el enlace de A para que señale a C. Si se elimina el primero o el último,
también se actualiza la referencia correspondiente. Eliminar el único nodo deja
`_primero` y `_ultimo` en `None` y la cantidad en cero.

### Por qué podemos usar un `for` con nuestra lista

`__iter__()` empieza en `_primero`, entrega su dato mediante `yield` y avanza al
nodo siguiente. `yield` pausa el recorrido hasta que el `for` solicite otro dato;
no crea una copia de todos los procesos.

```python
from estructuras import ListaEnlazada

nombres = ListaEnlazada()
nombres.agregar("Proceso A")
nombres.agregar("Proceso B")

for nombre in nombres:
    print(nombre)

nombres.eliminar("Proceso A")
assert len(nombres) == 1
assert list(nombres) == ["Proceso B"]
```

En los costos indicados, `n` es la cantidad de nodos: O(1) significa una cantidad
constante de operaciones; O(n) significa que puede ser necesario recorrer todos.

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
Reiniciar limpia los procesos y el reloj, conserva el divisor del quantum y la velocidad y continúa
la secuencia aleatoria; no vuelve a sembrar el generador.

## Cómo leer y explicar el algoritmo PMA-QMG-P

Empieza por `simulacion/planificador.py`:

1. `calcular_quantum()` divide el tiempo total del proceso entre el divisor
   configurado y redondea a múltiplos del paso de simulación.
2. `tiene_preferencia()` compara dos procesos con `if` y `else`: mayor prioridad,
   mayor quantum y llegada más antigua. Solo pasa al siguiente criterio si hay empate.
3. `seleccionar_siguiente_proceso()` recorre los preparados de la lista enlazada
   y conserva el mejor candidato. No mueve procesos ni modifica sus estados.
4. `ordenar_preparados()` inserta cada proceso en una lista temporal para mostrar
   las tarjetas en ese mismo orden. Usa `tiene_preferencia()` y conserva los
   empates completos. Esta ordenación por inserción cuesta O(n²) en el peor caso.

Ejemplo: A tiene prioridad 3 y quantum 200; B tiene prioridad 5 y quantum 100;
C tiene prioridad 5 y quantum 200. Gana C: supera a A por prioridad y a B por
quantum. Si otro proceso empata con C en ambos valores, gana el que llegó antes
a preparados. Cada regreso a preparados recibe un nuevo número de llegada.

### Qué significa el resultado de `tiene_preferencia()`

La llamada `tiene_preferencia(proceso_candidato, proceso_actual)` responde una
pregunta: ¿el candidato debe elegirse antes que el proceso actual?

- `True`: el candidato tiene preferencia.
- `False`: conservamos el proceso actual.

Los `if`, `elif` y `else` separan los criterios. Un `return` termina la comparación
inmediatamente; por eso una mayor prioridad gana aunque el quantum sea menor.
El orden de llegada solo se consulta cuando prioridad y quantum empatan.
Ya no se usan claves con números negativos.

### Ejemplo completo de selección

Supongamos que los preparados se recorren en este orden:

| Proceso | Prioridad | Quantum | Orden de llegada a preparados |
| --- | --- | --- | --- |
| A | 3 | 200 ms | 1 |
| B | 5 | 100 ms | 2 |
| C | 5 | 200 ms | 3 |
| D | 5 | 200 ms | 4 |

El recorrido de `seleccionar_siguiente_proceso()` funciona así:

1. `proceso_elegido` comienza en `None`: todavía no hay candidato guardado.
2. A es el primer proceso; se guarda provisionalmente como elegido.
3. B reemplaza a A porque tiene prioridad 5 frente a 3.
4. C reemplaza a B: empatan en prioridad, pero C tiene mayor quantum.
5. D no reemplaza a C: empatan en prioridad y quantum, pero C llegó antes.
6. La función devuelve C. Todavía no lo ha eliminado de preparados.

El motor recibe C en `_asignar_cpu_al_siguiente_proceso()`, lo elimina de la lista
preparados, cambia su estado a ejecución, reinicia su quantum usado y lo asigna a
`en_cpu`. También abre su segmento en el historial y registra su entrada a CPU.

Si la lista está vacía, la selección devuelve `None`. Si dos procesos empatan en
los tres criterios, se conserva el primero encontrado durante el recorrido.
`ordenar_preparados()` usa la misma comparación para que las tarjetas se muestren
en el orden C, D, B, A; no modifica los enlaces de la colección original.

### Qué representa `orden_cola`

Es un contador que el motor incrementa cada vez que un proceso entra a preparados.
No es el PID ni la hora de creación del proceso. Al volver de E/S o al agotar su
quantum recibe un nuevo número, para respetar su nueva llegada a esa colección.

### Cómo se calcula el quantum

El quantum es el máximo de tiempo de CPU que puede consumir un proceso en un turno.
Se calcula a partir de su **tiempo total original**, no del tiempo restante:

```text
quantum_sin_redondear = tiempo_total / divisor_quantum
cantidad_pasos = round(quantum_sin_redondear / TICK_MS)
quantum_redondeado = cantidad_pasos * TICK_MS
```

Si el resultado queda por debajo de `TICK_MS`, se usa `TICK_MS` como mínimo.
Actualmente el paso es 10 ms y el divisor predeterminado es 5:

| Tiempo total | Divisor | Quantum resultante |
| --- | --- | --- |
| 1000 ms | 5 | 200 ms |
| 530 ms | 5 | 110 ms |
| 15 ms | 5 | 10 ms |

`round()` redondea al entero más cercano; en un empate exacto termina en el entero
par. Por ejemplo, 100 ms con divisor 4 da 25 ms: `round(2.5)` produce 2 y el quantum
queda en 20 ms. El motor solo admite los divisores definidos en
`DIVISORES_QUANTUM`: 2, 3, 4, 5, 8 y 10.

### Cómo aplica el motor la selección

Después lee `paso()` en `simulacion/motor.py`. El motor aplica la selección y
administra el tiempo y los cambios de estado:

1. Llama a `preparar_ejecucion()`: si la CPU está libre, asigna el siguiente proceso.
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

### Cuándo se realiza la primera selección

Agregar procesos los deja en preparados, aunque la CPU esté libre. Esto permite
cargar varios antes de comenzar y compararlos por prioridad, quantum y llegada.
Por ejemplo, si primero agregas A con prioridad 1 y después B con prioridad 5,
ambos quedan esperando y B obtiene el primer turno al iniciar.

Mientras la CPU está libre, el panel muestra al próximo candidato y su BCP como
**PRÓXIMO PROCESO**. La vista se actualiza con el orden de preparados al agregar
procesos o cambiar el divisor del quantum. Es una vista previa: el proceso sigue
en preparados, el reloj no avanza y no se abre un segmento del historial. Si ya
hay un turno asignado, se muestra ese proceso incluso durante una pausa.

- **Iniciar:** el controlador llama a `motor.preparar_ejecucion()`, activa la
  reproducción y publica el estado elegido. La asignación no avanza el reloj;
  el temporizador ejecutará los siguientes pasos.
- **Paso:** el motor prepara la ejecución y avanza hasta 10 ms simulados.
- **Pausar y reanudar:** el proceso que ya tiene la CPU conserva su turno,
  su quantum usado y la E/S programada, aunque se agregue otro más prioritario.
- **Agregar durante la reproducción:** el nuevo proceso espera en preparados.
  Si la CPU está libre, podrá elegirse en el siguiente paso del temporizador.

Los cambios de turno durante un paso siguen ocurriendo cuando el proceso termina,
solicita E/S o agota su quantum. Las reglas de PMA-QMG-P permanecen iguales.

### Funciones del motor que conviene reconocer

| Función | Responsabilidad |
| --- | --- |
| `agregar_proceso()` | Valida los datos, crea el proceso y lo deja en preparados. No asigna la CPU. |
| `preparar_ejecucion()` | Al iniciar o dar un paso, selecciona un preparado si la CPU está libre. Conserva un turno ya asignado y no avanza el reloj. |
| `paso()` | Coordina el avance del tiempo y los cambios de estado. |
| `_tiempo_hasta_proximo_evento()` | Decide cuánto avanzar sin saltarse una finalización, un bloqueo o el fin de un quantum. |
| `_avanzar_reloj_y_tiempos()` | Acumula espera y ejecución, reduce la espera de E/S y extiende el historial. |
| `_reincorporar_procesos_con_entrada_salida_finalizada()` | Retira de suspendidos a quienes ya pueden volver a preparados. |
| `_resolver_estado_del_proceso_en_cpu()` | Comprueba si corresponde finalizar, suspender o devolver el proceso a preparados. |
| `_agregar_a_preparados()` | Actualiza el estado, el quantum y el nuevo orden de llegada. |
| `_asignar_cpu_al_siguiente_proceso()` | Solicita la selección al planificador y comienza el turno del elegido. |
| `_finalizar_proceso()` | Mueve el proceso terminado a la colección correspondiente y libera la CPU. |
| `_suspender_por_entrada_salida()` | Programa la duración del bloqueo y mueve el proceso a suspendidos. |
| `_devolver_por_quantum_agotado()` | Cierra el turno y devuelve el proceso a preparados. |

### Un paso puede contener varios cambios

Un paso permite avanzar **hasta 10 ms simulados**, pero no obliga a ejecutar
siempre los 10 ms con el mismo proceso. Si A solo necesita 3 ms más para terminar,
A ejecuta esos 3 ms, el motor lo finaliza y otro proceso puede usar los 7 ms
restantes del paso. Si no queda trabajo, el reloj se detiene en ese instante.

Mientras el tiempo avanza, los preparados acumulan espera y los suspendidos
reducen su bloqueo restante. El proceso en CPU acumula tiempo ejecutado y quantum
usado. Los procesos terminados ya no acumulan esos tiempos.

```text
Creación → Preparado → Ejecución → Terminado
               ↑           |
               |           +── Quantum agotado → Preparado
               |           |
               +── E/S finalizada ← Suspendido ← Solicitud de E/S
```

### Entrada/salida y porcentajes de progreso

Al comenzar un turno, `_programar_solicitud_entrada_salida()` usa la interactividad
como probabilidad de programar una solicitud de E/S. Si corresponde, sortea un
instante anterior al fin del quantum, en pasos de 10 ms. Un quantum de 10 ms no
programa una solicitud anticipada. El proceso también puede terminar antes de
llegar al instante sorteado.

La duración del bloqueo se sortea actualmente entre 100 y 400 ms, en múltiplos de
10 ms. Durante ese período el proceso no usa la CPU. Al terminar la espera vuelve
a preparados y participa nuevamente en la selección.

Las dos barras de la interfaz representan cantidades diferentes:

```text
Progreso del quantum = round(100 * quantum_usado / quantum)
Progreso total = round(100 * tiempo_ejecutado / tiempo_total)
```

Un proceso puede abandonar la CPU antes de consumir todo el quantum por E/S o por
finalización. Además, cuando agota el quantum, el motor puede comenzar el siguiente
turno antes de actualizar la pantalla; por eso no siempre se alcanza a ver el
100 % en la barra del turno anterior.

El reloj simulado es diferente de la velocidad de reproducción. El temporizador
llama a `paso()` cada 100 ms reales a velocidad 1×. Aumentar la velocidad hace esas
llamadas más frecuentes; no cambia la fórmula del quantum ni los criterios de selección.

## Reglas temporales conservadas

- Selección por prioridad más alta, quantum más grande y llegada a la cola.
- Un nuevo proceso con mayor prioridad no interrumpe el turno actual.
- Cada paso avanza hasta 10 ms y resuelve eventos en su instante exacto.
- El tiempo restante del paso puede usarse para el siguiente proceso.
- Al finalizar todos los procesos, la reproducción se detiene.
- Cambiar el divisor del quantum actualiza preparados y suspendidos; el proceso en CPU conserva
  el quantum y la E/S programados hasta terminar su turno.

## Pruebas

```sh
python -m unittest discover -s tests -v
```

| Archivo | Qué comprueba |
| --- | --- |
| `tests/test_motor.py` | Tiempos exactos, planificación, E/S y conservación de los procesos. |
| `tests/test_planificador.py` | Prioridad, quantum, llegada, empates y distintos órdenes de recorrido. |
| `tests/test_lista_enlazada.py` | Inserción, eliminación, recorridos y regreso simultáneo desde E/S. |
| `tests/test_controlador.py` | Reproducción, mensajes y reinicio. |
| `tests/test_interfaz.py` | Controles, selección y dibujo sin abrir una pantalla visible. |
| `tests/test_historial_gantt.py` | Zoom, desplazamiento, seguimiento y reinicio del historial. |
| `tests/test_independencia_motor.py` | Ejecución sin Qt y generación reproducible con semilla. |

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

## Referencia rápida para explicar el proyecto

- **¿Dónde está PMA-QMG-P?** En `tiene_preferencia()`, dentro de
  `simulacion/planificador.py`. La CPU aplica su resultado al quedar libre.
- **¿Dónde se recorren los candidatos?** En `seleccionar_siguiente_proceso()`,
  que conserva el mejor encontrado sin modificar la lista enlazada.
- **¿La lista enlazada se mantiene ordenada?** Conserva el orden de inserción.
  La selección recorre todos los candidatos; las tarjetas usan una copia ordenada.
- **¿Puede haber dos procesos en CPU?** No. `en_cpu` contiene uno o `None`.
- **¿Un proceso nuevo interrumpe al actual?** No. Espera hasta que la CPU quede libre.
- **¿Qué pasa al agotar el quantum?** Vuelve a preparados con un nuevo orden de llegada.
- **¿Quién cambia los estados?** El motor. El planificador decide la preferencia y
  la interfaz representa los resultados.
- **¿Se explican las decisiones con mensajes detallados?** Se registra la entrada
  a CPU, pero la función `explicar_seleccion()` fue retirada. La barra inferior
  muestra el último evento recibido y no conserva un historial visible de mensajes.
- **¿Por qué estos tres archivos no tienen anotaciones de tipos?** El motor, el
  planificador y la lista enlazada usan nombres descriptivos y pasos explícitos
  para facilitar su lectura; los objetos y el comportamiento siguen siendo los mismos.
