from datetime import date
from itertools import groupby

from matafuegos.exceptions import (
    RangoDeFechasInvalidoException,
    SinMatafuegosParaAlertaException,
    SinMatafuegosParaInformeException,
)
from matafuegos.models import Matafuegos
from reports.services import render_report_pdf, report_header_context


def _agrupar_por_cliente(queryset):
    return [
        {'cliente': cliente, 'items': list(items)}
        for cliente, items in groupby(queryset, key=lambda d: d.cliente)
    ]


def generar_listado_matafuegos(queryset):
    matafuegos = list(queryset)
    context = report_header_context(matafuegos[0] if matafuegos else None, 'Listado de matafuegos')
    context['matafuegos'] = matafuegos
    return render_report_pdf('reports/listado_matafuegos.html', context)


def emitir_alerta_vencimientos(matafuegos, fecha_inicio, fecha_fin):
    """Informe de vencimientos entre dos fechas. `fecha_inicio`/`fecha_fin` se
    comparan tal cual (strings ISO 'YYYY-MM-DD' comparan correctamente como
    texto), igual que el comportamiento previo."""
    if fecha_inicio > fecha_fin:
        raise RangoDeFechasInvalidoException('La fecha de fin debe ser mayor a la de inicio.')
    lista = list(matafuegos)
    if not lista:
        raise SinMatafuegosParaAlertaException('No hay matafuegos con vencimiento entre las fechas.')
    context = report_header_context(lista[0], 'Alerta de vencimientos')
    context.update({'lista': lista, 'fecha_inicio': fecha_inicio, 'fecha_fin': fecha_fin})
    return render_report_pdf('reports/alerta_vencimientos.html', context)


def emitir_informe_proximos_vencimientos(carga, ph):
    carga = list(carga)
    ph = list(ph)
    if not carga and not ph:
        raise SinMatafuegosParaInformeException('No hay matafuegos con vencimiento en los proximos 30 dias.')
    primero = carga[0] if carga else ph[0]
    context = report_header_context(primero, 'Próximos vencimientos')
    context.update({
        'grupos_carga': _agrupar_por_cliente(carga),
        'grupos_ph': _agrupar_por_cliente(ph),
    })
    return render_report_pdf('reports/proximos_vencimientos.html', context)


def marcar_vencidos():
    """Marca vencido=True a los matafuegos con más de 21 años desde su fecha
    de fabricación. Corre a diario vía django-crontab (ver matafuegos/tasks.py)."""
    for matafuego in Matafuegos.objects.exclude(fecha_fabricacion=None):
        if (date.today() - matafuego.fecha_fabricacion).days / 365 > 21:
            matafuego.vencido = True
            matafuego.save()


def eliminar_matafuego(matafuego):
    """Si el matafuego ya tiene órdenes de trabajo asociadas, un delete físico
    las arrastraría en cascada (Ordenes_de_trabajo.matafuegos usa
    on_delete=CASCADE) -- en ese caso se hace baja lógica (estado='i') para
    conservar el historial. Si no tiene ninguna, se elimina físicamente.
    Devuelve True si se eliminó físicamente, False si se dio de baja."""
    if matafuego.ordenes_de_trabajo.exists():
        matafuego.estado = 'i'
        matafuego.save(update_fields=['estado'])
        return False
    matafuego.delete()
    return True


def activar_matafuego(matafuego):
    matafuego.estado = 'a'
    matafuego.save(update_fields=['estado'])
