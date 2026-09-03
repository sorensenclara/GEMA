from django.db.models import Case, F, FloatField, Sum, When

from orden_trabajo.models import TareaOrden


def calcular_monto(orden):
    """Suma el precio de cada TareaOrden de la orden: el precio ajustado
    (`precioAj`) si se cargó uno distinto de cero, si no el precio de lista
    de la tarea. Agregación SQL en una sola query -- la versión anterior
    hacía 2 queries por cada TareaOrden dentro de un loop en Python."""
    total = TareaOrden.objects.filter(orden=orden).aggregate(
        total=Sum(
            Case(
                When(precioAj=0.0, then=F('tarea__precio')),
                default=F('precioAj'),
                output_field=FloatField(),
            )
        )
    )['total']
    return total or 0
