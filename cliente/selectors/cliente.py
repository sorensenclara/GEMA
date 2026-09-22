from datetime import date, timedelta

from django.db.models import Q

from cliente.models import Cliente


def list_clientes(company, q=None):
    qs = Cliente.objects.filter(company=company).order_by('nombre')
    if q:
        qs = qs.filter(Q(nombre__icontains=q) | Q(codigo__icontains=q) | Q(cuit_cuil__icontains=q))
    return qs


def count_clientes_activos(company):
    return Cliente.objects.filter(company=company, estado='a').count()


def count_clientes_sin_actividad(company, dias=90):
    """Clientes con al menos un matafuego vencido que no tienen ninguna
    orden de trabajo en los ultimos `dias` dias -- o sea, no renovaron ni
    pasaron por el taller a pesar de tener matafuegos vencidos. Pensado para
    el panel "Requieren atencion" del dashboard (ver charla con Clara,
    2026-09-22): sirve para saber a quien contactar.

    Ojo: "orden de trabajo" es la unica senial de actividad que hoy modela
    el sistema -- si en el futuro se agrega otro tipo de contacto con el
    cliente (llamada, visita sin orden, etc.) esta consulta va a quedar
    corta y hay que sumarlo aca.
    """
    limite = date.today() - timedelta(days=dias)
    return Cliente.objects.filter(
        company=company,
        matafuegos__vencido=True,
    ).exclude(
        ordenes_de_trabajo__fecha_creacion__gte=limite,
    ).distinct().count()
