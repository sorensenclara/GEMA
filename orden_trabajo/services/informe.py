from orden_trabajo.exceptions import (
    RangoDeFechasInvalidoException,
    SinHistorialParaInformeException,
    SinRecargasParaInformeException,
)
from orden_trabajo.models import TareaOrden
from reports.services import render_report_pdf, report_header_context


def emitir_informe_orden(orden):
    """Informe con toda la información y tareas de una orden de trabajo."""
    context = report_header_context(orden, 'Informe de la orden de trabajo')
    context.update({
        'orden': orden,
        'tareas': TareaOrden.objects.filter(orden=orden.id),
    })
    return render_report_pdf('reports/informe_orden.html', context)


def emitir_informe_recargas(ordenes, fecha_desde, fecha_hasta):
    """Listado de matafuegos recargados (oblea DPS ya emitida) entre dos
    fechas de cierre de orden. `fecha_desde`/`fecha_hasta` se comparan tal
    cual (strings ISO 'YYYY-MM-DD' comparan correctamente como texto), igual
    que emitir_alerta_vencimientos en matafuegos/services/matafuegos.py."""
    if fecha_desde > fecha_hasta:
        raise RangoDeFechasInvalidoException('La fecha hasta debe ser mayor a la fecha desde.')
    ordenes = list(ordenes)
    if not ordenes:
        raise SinRecargasParaInformeException('No hay matafuegos recargados entre las fechas indicadas.')
    filas = []
    for orden in ordenes:
        tareas_recarga = TareaOrden.objects.filter(orden=orden, tarea__es_recarga=True).select_related('tarea')
        nombres_tarea = dict.fromkeys(t.tarea.nombre for t in tareas_recarga)
        filas.append({
            'fecha_cierre': orden.fecha_cierre,
            'matafuego': orden.matafuegos,
            'cliente': orden.cliente,
            'tarea': ', '.join(nombres_tarea),
        })
    context = report_header_context(ordenes[0], 'Informe de recargas')
    context.update({'filas': filas, 'fecha_desde': fecha_desde, 'fecha_hasta': fecha_hasta})
    return render_report_pdf('reports/informe_recargas.html', context)


def emitir_informe_historico_matafuego(matafuego):
    """Historial de tareas realizadas sobre un matafuego a lo largo de todas
    sus ordenes de trabajo cerradas, de la mas reciente a la mas vieja. El
    N° de DPS solo se muestra en las filas de tareas de recarga (ver
    `_actualizar_matafuego_y_marcar_impresa` en `orden_trabajo/services/oblea.py`,
    que es donde se persiste `Ordenes_de_trabajo.numero_dps` al emitir la
    oblea)."""
    tareas = (
        TareaOrden.objects.filter(orden__matafuegos=matafuego, orden__fecha_cierre__isnull=False)
        .select_related('tarea', 'orden')
        .order_by('-orden__fecha_cierre', '-orden_id')
    )
    filas = [{
        'fecha_cierre': t.orden.fecha_cierre,
        'orden_id': t.orden_id,
        'tarea': t.tarea.nombre,
        'numero_dps': t.orden.numero_dps if t.tarea.es_recarga else None,
    } for t in tareas]
    if not filas:
        raise SinHistorialParaInformeException('El matafuego no tiene ordenes de trabajo cerradas.')
    context = report_header_context(matafuego, 'Informe historico del matafuego')
    context.update({'matafuego': matafuego, 'cliente': matafuego.cliente, 'filas': filas})
    return render_report_pdf('reports/informe_historico_matafuego.html', context)
