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


def list_ordenes_recargadas_entre(company, fecha_desde, fecha_hasta):
    """Órdenes con oblea DPS ya emitida (estado 'i' o, si ya se facturaron,
    'fac') cerradas entre las fechas indicadas -- la fecha de cierre es la
    misma que se usa como fecha de emisión de la oblea (ver
    orden_trabajo/services/oblea.py)."""
    return Ordenes_de_trabajo.objects.filter(
        company=company, estado__in=('i', 'fac'), fecha_cierre__range=(fecha_desde, fecha_hasta),
    ).select_related('cliente', 'matafuegos', 'matafuegos__tipo', 'matafuegos__marca').order_by('fecha_cierre', 'cliente__nombre')


def count_ordenes_pendientes(company):
    return Ordenes_de_trabajo.objects.filter(company=company, estado='p').count()


def ordenes_por_estado(company, periodo_dias=None):
    """Cantidad de órdenes de la compañía agrupadas por estado, para el
    gráfico del dashboard. `periodo_dias` (30/60/90, o None = todo el
    historial) filtra por `fecha_creacion` -- es la fecha de negocio de la
    orden (la que carga/ve el usuario), no `created_at` de AuditModel (esa
    es la fecha de auditoría de cuándo se guardó el registro)."""
    qs = Ordenes_de_trabajo.objects.filter(company=company)
    if periodo_dias:
        qs = qs.filter(fecha_creacion__gte=date.today() - timedelta(days=periodo_dias))
    return qs.values('estado').annotate(total=Count('id')).order_by('estado')
