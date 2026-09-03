from datetime import date

from orden_trabajo.exceptions import TransicionDeEstadoInvalidaException
from orden_trabajo.selectors import calcular_monto


def recalcular_monto_total(orden):
    """Recalcula y persiste `monto_total` a partir de las TareaOrden actuales
    de la orden. Se llama explícitamente después de guardar el formset de
    tareas -- ya no es un side-effect oculto de `Ordenes_de_trabajo.save()`."""
    orden.monto_total = calcular_monto(orden)
    orden.save(update_fields=['monto_total'])
    return orden


def _transicionar(orden, estados_origen, estado_destino, **campos_extra):
    if orden.estado not in estados_origen:
        raise TransicionDeEstadoInvalidaException(
            f'La orden N° {orden.id} está en estado "{orden.get_estado_display()}", '
            'no se puede aplicar esta acción desde ahí.'
        )
    orden.estado = estado_destino
    for campo, valor in campos_extra.items():
        setattr(orden, campo, valor)
    orden.save()
    return orden


def iniciar_orden(orden):
    """Pendiente -> En proceso."""
    return _transicionar(orden, ['p'], 'ep')


def finalizar_orden(orden):
    """En proceso -> Finalizada, con fecha de cierre de hoy (igual que la
    antigua acción de admin `action_finalizada`)."""
    return _transicionar(orden, ['ep'], 'f', fecha_cierre=date.today())


def cancelar_orden(orden):
    """En proceso -> Cancelada."""
    return _transicionar(orden, ['ep'], 'c')


def facturar_orden(orden):
    """Impresa -> Facturada."""
    return _transicionar(orden, ['i'], 'fac')
