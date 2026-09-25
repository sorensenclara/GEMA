import csv
import io
from datetime import date
from itertools import groupby

from matafuegos.exceptions import (
    RangoDeFechasInvalidoException,
    SinMatafuegosParaAlertaException,
    SinMatafuegosParaInformeException,
)
from matafuegos.models import Matafuegos, NotificacionVencimiento
from reports.services import render_report_pdf, report_header_context


_ESTADO_VENCIMIENTO_DISPLAY = {
    'al_dia': 'Al día',
    'proximo': 'Próximo a vencer',
    'vencido': 'Vencido',
}

_ESTADO_NOTIFICACION_DISPLAY = {
    None: 'Sin notificar',
    NotificacionVencimiento.ESTADO_PENDIENTE: 'Pendiente de confirmación',
    NotificacionVencimiento.ESTADO_NOTIFICADA: 'Notificado',
    NotificacionVencimiento.ESTADO_ERROR: 'Error',
}


def exportar_panel_vencimientos_csv(filas):
    """CSV de las filas del panel de Vencimientos (las que están filtradas
    y buscadas en pantalla en ese momento, sin recortar por paginación --
    la exportación siempre trae el conjunto completo que se está mirando).
    Se genera con el módulo csv de la biblioteca estándar, sin depender de
    ningún paquete nuevo; el archivo abre bien en Excel/Sheets."""
    buffer = io.StringIO()
    writer = csv.writer(buffer, delimiter=';')
    writer.writerow([
        'Cliente', 'Código cliente', 'Matafuego N°', 'Tipo', 'Tipo de vencimiento',
        'Fecha de vencimiento', 'Estado de vencimiento', 'Estado de notificación',
        'Teléfono', 'Último aviso',
    ])
    for fila in filas:
        matafuego = fila['matafuego']
        notificacion = fila['notificacion']
        writer.writerow([
            matafuego.cliente.nombre,
            matafuego.cliente.codigo,
            matafuego.numero,
            str(matafuego.tipo),
            dict(NotificacionVencimiento.TIPOS_VENCIMIENTO).get(fila['tipo_vencimiento'], fila['tipo_vencimiento']),
            fila['fecha_vencimiento'].strftime('%d/%m/%Y'),
            _ESTADO_VENCIMIENTO_DISPLAY.get(fila['estado_vencimiento'], ''),
            _ESTADO_NOTIFICACION_DISPLAY.get(fila['estado_notificacion'], ''),
            matafuego.cliente.telefono or '',
            notificacion.updated_at.strftime('%d/%m/%Y %H:%M') if notificacion else '',
        ])
    return buffer.getvalue().encode('utf-8-sig')  # BOM para que Excel detecte UTF-8


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
