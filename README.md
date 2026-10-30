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
