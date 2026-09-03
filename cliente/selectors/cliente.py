from django.db.models import Q

from cliente.models import Cliente


def list_clientes(company, q=None):
    qs = Cliente.objects.filter(company=company).order_by('nombre')
    if q:
        qs = qs.filter(Q(nombre__icontains=q) | Q(codigo__icontains=q) | Q(cuit_cuil__icontains=q))
    return qs


def count_clientes_activos(company):
    return Cliente.objects.filter(company=company, estado='a').count()
