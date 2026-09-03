from datetime import date, timedelta

from django.db.models import Count

from orden_trabajo.models import Ordenes_de_trabajo


def list_ordenes(company, estado=None, tipo_matafuego=None, categoria_matafuego=None):
    qs = Ordenes_de_trabajo.objects.filter(company=company).select_related('cliente', 'matafuegos').order_by('-fecha_cierre', '-id')
    if estado:
        qs = qs.filter(estado=estado)
    if tipo_matafuego:
        qs = qs.filter(matafuegos__tipo_id=tipo_matafuego)
    if categoria_matafuego:
        qs = qs.filter(matafuegos__categoria=categoria_matafuego)
    return qs


def list_ordenes_ultima_semana(company):
    today = date.today()
    td = timedelta(7)
    return Ordenes_de_trabajo.objects.filter(
        company=company, estado='i', fecha_cierre__range=(today - td, today),
    ).order_by('cliente')


def count_ordenes_pendientes(company):
    return Ordenes_de_trabajo.objects.filter(company=company, estado='p').count()


def ordenes_por_estado(company):
    """Cantidad de órdenes de la compañía agrupadas por estado, para el
    gráfico del dashboard."""
    return (
        Ordenes_de_trabajo.objects.filter(company=company)
        .values('estado').annotate(total=Count('id')).order_by('estado')
    )
