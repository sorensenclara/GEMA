"""Flujo de notificación de vencimiento por WhatsApp, vía enlaces `wa.me`
(sin WhatsApp Cloud API ni ningún servicio pago -- ver Etapa 1/14 de la
propuesta). El envío nunca es automático: acá solo se arma el enlace y se
administra el registro de NotificacionVencimiento en sus dos pasos
manuales (PENDIENTE al abrir el enlace, NOTIFICADA/ERROR al volver y
confirmar)."""

from dataclasses import dataclass
from urllib.parse import quote

from core.utils import es_telefono_normalizado
from matafuegos.exceptions import (
    ClienteSinWhatsAppException,
    MatafuegoSinVencimientoException,
)
from matafuegos.models import NotificacionVencimiento
from matafuegos.selectors.matafuegos import vencimiento_relevante

_DESCRIPCION_VENCIMIENTO = {
    NotificacionVencimiento.TIPO_CARGA: 'vencimiento de carga',
    NotificacionVencimiento.TIPO_PH: 'vencimiento de prueba hidráulica',
}


@dataclass
class NotificacionPreview:
    """Todo lo que necesita el modal de confirmación: a qué ciclo de
    vencimiento corresponde, el teléfono que se va a usar, el mensaje
    exacto y el enlace `wa.me` ya armado."""
    tipo_vencimiento: str
    tipo_vencimiento_display: str
    fecha_vencimiento: object
    telefono: str
    mensaje: str
    link_whatsapp: str


def construir_mensaje(matafuego, tipo_vencimiento, fecha_vencimiento):
    descripcion = _DESCRIPCION_VENCIMIENTO[tipo_vencimiento]
    return (
        f'Hola {matafuego.cliente.nombre}, te contactamos desde {matafuego.company.nombre}. '
        f'Te informamos que el matafuego N° {matafuego.numero} tiene {descripcion} '
        f'el {fecha_vencimiento.strftime("%d/%m/%Y")}. '
        'Comunicate con nosotros para coordinar su revisión/recarga. Muchas gracias.'
    )


def preparar_notificacion(matafuego):
    """Resuelve todo lo necesario para mostrar el modal de Notificar.
    Levanta ClienteSinWhatsAppException si el cliente no tiene un teléfono
    válido (la vista debe mostrar "Cliente sin WhatsApp registrado" con un
    link para editarlo, nunca un botón que parezca activo), o
    MatafuegoSinVencimientoException si el matafuego no tiene ningún
    vencimiento próximo que notificar."""
    telefono = matafuego.cliente.telefono
    if not es_telefono_normalizado(telefono):
        raise ClienteSinWhatsAppException(
            f'{matafuego.cliente.nombre} no tiene un WhatsApp válido registrado.'
        )
    tipo_vencimiento, fecha_vencimiento = vencimiento_relevante(matafuego)
    if not fecha_vencimiento:
        raise MatafuegoSinVencimientoException(
            f'El matafuego N° {matafuego.numero} no tiene ningún vencimiento próximo.'
        )
    mensaje = construir_mensaje(matafuego, tipo_vencimiento, fecha_vencimiento)
    link = f'https://wa.me/{telefono}?text={quote(mensaje)}'
    return NotificacionPreview(
        tipo_vencimiento=tipo_vencimiento,
        tipo_vencimiento_display=dict(NotificacionVencimiento.TIPOS_VENCIMIENTO)[tipo_vencimiento],
        fecha_vencimiento=fecha_vencimiento,
        telefono=telefono,
        mensaje=mensaje,
        link_whatsapp=link,
    )


def crear_o_reutilizar_pendiente(matafuego, preview):
    """Se llama al confirmar el modal y abrir el enlace `wa.me`. Si ya
    había una notificación PENDIENTE sin cerrar para este mismo ciclo de
    vencimiento, la reutiliza (actualiza teléfono/mensaje por si cambiaron)
    en vez de crear una duplicada. Si la última notificación de este ciclo
    ya está cerrada (NOTIFICADA o ERROR), o no hay ninguna todavía, crea un
    registro nuevo -- nunca se reabre ni se sobrescribe un intento ya
    cerrado."""
    pendiente = matafuego.notificaciones.filter(
        tipo_vencimiento=preview.tipo_vencimiento,
        fecha_vencimiento=preview.fecha_vencimiento,
        estado_envio=NotificacionVencimiento.ESTADO_PENDIENTE,
    ).order_by('-created_at').first()
    if pendiente:
        pendiente.numero_destino = preview.telefono
        pendiente.mensaje = preview.mensaje
        pendiente.save(update_fields=['numero_destino', 'mensaje', 'updated_at', 'updated_by'])
        return pendiente
    return NotificacionVencimiento.objects.create(
        matafuego=matafuego,
        tipo_vencimiento=preview.tipo_vencimiento,
        fecha_vencimiento=preview.fecha_vencimiento,
        numero_destino=preview.telefono,
        mensaje=preview.mensaje,
        estado_envio=NotificacionVencimiento.ESTADO_PENDIENTE,
    )


def marcar_enviado(notificacion):
    """Cierra el intento como NOTIFICADA -- éste, y solo éste, es el
    estado que cuenta como "Notificado" en filtros y dashboard."""
    notificacion.estado_envio = NotificacionVencimiento.ESTADO_NOTIFICADA
    notificacion.save(update_fields=['estado_envio', 'updated_at', 'updated_by'])


def marcar_error(notificacion, observacion=''):
    """Cierra el intento como ERROR (el envío no se concretó). No cuenta
    como notificado; un reintento posterior crea un registro nuevo (ver
    crear_o_reutilizar_pendiente)."""
    notificacion.estado_envio = NotificacionVencimiento.ESTADO_ERROR
    if observacion:
        notificacion.observacion = observacion
    notificacion.save(update_fields=['estado_envio', 'observacion', 'updated_at', 'updated_by'])
