"""Formato de textos (sin Qt): tiempos y HTML de los tooltips."""
from html import escape

from interfaz.estilos import colores


def formatear_milisegundos(valor: int) -> str:
    """1500 -> '1.500 ms'"""
    return f"{valor:,} ms".replace(",", ".")


def tooltip_proceso(proceso, segmento=None) -> str:
    """Info de un proceso para mostrar al pasar el mouse.
    `segmento` (opcional) agrega los datos del segmento del Gantt bajo el cursor."""
    estado = colores.color_estado(proceso.estado)
    filas = [
        f"<b style='color:{colores.color_pid(proceso.pid)}'>{escape(proceso.nombre)}</b> &nbsp;(PID {proceso.pid})",
        f"Estado: <b style='color:{estado}'>{proceso.estado.value}</b>",
        f"Prioridad: {proceso.prioridad} &nbsp;·&nbsp; Quantum: {formatear_milisegundos(proceso.quantum)}",
        f"Ejecutado: {formatear_milisegundos(proceso.tiempo_ejecutado)} / {formatear_milisegundos(proceso.tiempo_total)} ({proceso.progreso_total}%)",
        f"Interactividad: {proceso.interactividad}%",
    ]
    if proceso.causa_bloqueo and proceso.estado.name == "SUSPENDIDO":
        filas.append(f"Bloqueado por: {proceso.causa_bloqueo} ({formatear_milisegundos(proceso.tiempo_en_bloqueo)} / {formatear_milisegundos(proceso.bloqueo_total)})")
    if segmento is not None:
        filas.append(f"<br>Turno: {formatear_milisegundos(segmento.inicio)} → {formatear_milisegundos(segmento.fin)} (duró {formatear_milisegundos(segmento.duracion)})")
    return "<br>".join(filas)
