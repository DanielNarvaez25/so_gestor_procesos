# so_gestor_procesos
Simulador de gestor de procesos (planificador PMA-QMG-P) con PySide6.

## Ejecutar
```
pip install -r requirements.txt
python main.py
```

## Estructura
```
main.py                  punto de entrada
core/                    lógica de la simulación (sin widgets)
  config.py              parámetros: tick, prioridades, ratas, ventana del Gantt
  simulation.py          motor (QTimer + señales)
  scheduler.py           algoritmo de planificación
  process.py / states.py / timeline.py
ui/
  main_window.py         arma los paneles y los conecta con la simulación
  widgets/
    panel.py             contenedor base con título
    toolbar.py           agregar, iniciar/pausar, reiniciar, rata de quantum
    process_form.py      formulario lateral (nombre, prioridad, aleatorio)
    queue_panel.py       cola de tarjetas (Preparados / Ejecución / Suspendidos)
    process_card.py      tarjeta de un proceso (tooltip con su info)
    cpu_panel.py         proceso en CPU + progreso del quantum
    gantt_view.py        línea de tiempo (tooltip al pasar sobre las barras)
    bcp_campos.py        QUÉ datos del BCP se muestran en cada panel/tabla
    bcp_panel.py         detalle de un BCP (Ejecución / Seleccionado)
    bcp_table.py         tablas BCP Preparados / Suspendidos
utils/
  colors.py              PALETA CENTRAL: todos los colores viven aquí
  theme.py               carga el QSS reemplazando {{VARIABLE}} por colors.py
  formato.py             textos de tiempo y HTML de los tooltips
  random_generator.py
resources/styles/dark.qss  estilos (solo usa {{VARIABLES}}, nunca colores fijos)
```

## Cambiar colores
Edita solo `utils/colors.py`. El QSS y el Gantt leen de ahí; no hay colores escritos en otro lado.


## Interfaz y controles (rama juan)
- Tablero oscuro con indicadores de reloj, preparados, E/S y terminados.
- Formulario: nombre opcional, prioridad, tiempo de CPU exacto en ms y probabilidad de E/S por turno.
- Iniciar / Pausar, avance de hasta 10 ms por paso y velocidad de reproducción de 0,5× a 4×.
- Colas en pestañas: Listos, E/S y Fin. Selecciona un proceso para consultar su BCP en el Inspector.
- Gantt con PID por fila, desplazamiento temporal automático y tooltips por segmento.
- Pestañas de BCP preparados, BCP suspendidos y registro de los últimos 1.000 eventos.
- Panel lateral ocultable y divisores ajustables. Tamaño mínimo: 1100 × 820.

## Reglas de tiempo y quantum
El orden de planificación sigue siendo prioridad más alta, quantum más grande y llegada a la cola.
La incorporación de un proceso con más prioridad no interrumpe el turno en curso.
Cada paso avanza hasta 10 ms simulados; los eventos intermedios se resuelven en su instante exacto.
Por ejemplo, un proceso de 15 ms registra exactamente 15 ms de CPU y de Gantt.
El tiempo sobrante de un tick puede utilizarse para el siguiente proceso.
Cuando no quedan procesos activos, el reloj se detiene automáticamente.

Cambiar la rata actualiza los procesos preparados o suspendidos. El proceso en CPU conserva el
quantum y la solicitud de E/S de su turno actual, y adopta la nueva rata al volver a la cola.
Esto evita reprogramar un bloqueo a mitad de turno. Reiniciar conserva la rata y velocidad elegidas.

## Pruebas
Desde la raíz del repositorio, con las dependencias instaladas:
```
python -m unittest discover -s tests -v
```
Incluyen tiempos no múltiplos del tick, reutilización del resto del tick, orden de planificación,
bloqueos de E/S, cambio de rata, reinicio, controles y ejecuciones con semillas reproducibles.
