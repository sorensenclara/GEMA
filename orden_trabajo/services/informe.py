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
