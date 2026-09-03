from datetime import date
from itertools import groupby

from orden_trabajo.exceptions import SinOrdenesParaFacturarException
from orden_trabajo.models import TareaOrden
from reports.services import render_report_pdf, report_header_context


def _precio_efectivo(tarea_orden):
    """Precio ajustado (`precioAj`) si se cargó uno distinto de cero, si no
    el precio de lista de la tarea -- misma regla que
    selectors/tarea_orden.py::calcular_monto."""
    return tarea_orden.precioAj or tarea_orden.tarea.precio


def _agregar_tareas_por_cliente(ordenes_cliente):
    """Cuenta cuántas veces se repite cada combinación (tarea, cantidad
    cargada, tipo de matafuego) entre las órdenes de un mismo cliente, y
    suma el precio efectivo de cada repetición (no precio_unitario*cantidad:
    así el subtotal es correcto aunque el precio ajustado difiera entre
    repeticiones de la misma combinación)."""
    conteo = {}
    subtotales = {}
    for orden in ordenes_cliente:
        tareas = TareaOrden.objects.filter(orden=orden.id).order_by('tarea__nombre')
        for t in tareas:
            clave = (t.tarea.nombre, str(t.cant_cargada), str(orden.matafuegos.tipo))
            conteo[clave] = conteo.get(clave, 0) + 1
            subtotales[clave] = subtotales.get(clave, 0) + _precio_efectivo(t)
    return conteo, subtotales


def emitir_informe_facturacion(ordenes):
    """Informe de facturación: cuenta tareas repetidas por cliente, agrupadas,
    con el precio de cada línea y el total a facturar por cliente."""
    ordenes = list(ordenes.order_by('cliente__nombre'))
    if not ordenes:
        raise SinOrdenesParaFacturarException('Debe seleccionar al menos una orden.')
    grupos = []
    for cliente, ordenes_cliente in groupby(ordenes, key=lambda o: o.cliente):
        conteo, subtotales = _agregar_tareas_por_cliente(ordenes_cliente)
        if not conteo:
            continue
        filas = [
            {
                'cantidad': cantidad, 'tarea': tarea, 'cant_cargada': cant_cargada,
                'tipo': tipo, 'precio': subtotales[(tarea, cant_cargada, tipo)],
            }
            for (tarea, cant_cargada, tipo), cantidad in conteo.items()
        ]
        grupos.append({'cliente': cliente, 'filas': filas, 'total': sum(subtotales.values())})
    context = report_header_context(ordenes[0], 'Informe facturación')
    context.update({'grupos': grupos, 'fecha': date.today(), 'total_general': sum(g['total'] for g in grupos)})
    return render_report_pdf('reports/informe_facturacion.html', context)


def emitir_informe_facturacion_ultima_semana(ordenes):
    """Informe de facturación de la última semana: detalle línea por línea,
    a diferencia de emitir_informe_facturacion (que cuenta repeticiones), con
    el precio de cada línea y el total a facturar por cliente."""
    ordenes = list(ordenes)
    if not ordenes:
        raise SinOrdenesParaFacturarException('No hay ordenes finalizadas durante la ultima semana.')
    grupos = []
    for cliente, ordenes_cliente in groupby(ordenes, key=lambda o: o.cliente):
        filas = []
        total_cliente = 0
        for orden in ordenes_cliente:
            tareas = TareaOrden.objects.filter(orden=orden.id)
            for i, t in enumerate(tareas):
                precio = _precio_efectivo(t)
                total_cliente += precio
                filas.append({'orden': orden, 'tarea': t, 'primera': i == 0, 'precio': precio})
        if filas:
            grupos.append({'cliente': cliente, 'filas': filas, 'total': total_cliente})
    context = report_header_context(ordenes[0], 'Informe facturación última semana')
    context.update({'grupos': grupos, 'fecha': date.today(), 'total_general': sum(g['total'] for g in grupos)})
    return render_report_pdf('reports/informe_facturacion_semana.html', context)
