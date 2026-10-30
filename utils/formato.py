"""Formato de textos (sin Qt): tiempos y HTML de los tooltips."""
from html import escape

from . import colors


def ms(valor: int) -> str:
    """1500 -> '1.500 ms'"""
    return f"{valor:,} ms".replace(",", ".")


def tooltip_proceso(p, seg=None) -> str:
    """Info de un proceso para mostrar al pasar el mouse.
    `seg` (opcional) agrega los datos del segmento del Gantt bajo el cursor."""
    estado = colors.color_estado(p.estado)
    filas = [
        f"<b style='color:{p.color}'>{escape(p.nombre)}</b> &nbsp;(PID {p.pid})",
        f"Estado: <b style='color:{estado}'>{p.estado.value}</b>",
        f"Prioridad: {p.prioridad} &nbsp;·&nbsp; Quantum: {ms(p.quantum)}",
        f"Ejecutado: {ms(p.tiempo_ejecutado)} / {ms(p.tiempo_total)} ({p.progreso_total}%)",
        f"Interactividad: {p.interactividad}%",
    ]
    if p.causa_bloqueo and p.estado.name == "SUSPENDIDO":
        filas.append(f"Bloqueado por: {p.causa_bloqueo} ({ms(p.tiempo_en_bloqueo)} / {ms(p.bloqueo_total)})")
    if seg is not None:
        filas.append(f"<br>Turno: {ms(seg.inicio)} → {ms(seg.fin)} (duró {ms(seg.duracion)})")
    return "<br>".join(filas)
