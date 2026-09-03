from datetime import date, timedelta

from django.db.models import Q

from matafuegos.models import Matafuegos


def list_matafuegos(company, q=None, tipo=None, estado=None, vencido=None):
    qs = Matafuegos.objects.filter(company=company).select_related('cliente', 'tipo').order_by('numero')
    if q:
        qs = qs.filter(Q(numero__icontains=q) | Q(cliente__nombre__icontains=q) | Q(numero_dps__icontains=q))
    if tipo:
        qs = qs.filter(tipo_id=tipo)
    if estado:
        qs = qs.filter(estado=estado)
    if vencido:
        qs = qs.filter(vencido=vencido == '1')
    return qs


def list_vencimiento_entre(company, fecha_inicio, fecha_fin):
    return Matafuegos.objects.filter(
        company=company, fecha_proxima_carga__range=(fecha_inicio, fecha_fin),
    ).order_by('categoria', 'cliente__nombre')


def list_proximos_vencimientos_carga(company, dias=30):
    today = date.today()
    return Matafuegos.objects.filter(
        company=company, fecha_proxima_carga__range=(today, today + timedelta(dias)),
    ).order_by('categoria', 'cliente__nombre')


def list_proximos_vencimientos_ph(company, dias=30):
    today = date.today()
    return Matafuegos.objects.filter(
        company=company, fecha_proxima_ph__range=(today, today + timedelta(dias)),
    ).order_by('categoria', 'cliente__nombre')


def matafuegos_de_cliente(cliente):
    return Matafuegos.objects.filter(cliente=cliente).order_by('numero')


def count_matafuegos(company):
    return Matafuegos.objects.filter(company=company).count()


def count_vencimiento_proximo(company, dias=30):
    today = date.today()
    horizon = today + timedelta(dias)
    return Matafuegos.objects.filter(company=company).filter(
        Q(fecha_proxima_carga__range=(today, horizon)) | Q(fecha_proxima_ph__range=(today, horizon))
    ).distinct().count()
