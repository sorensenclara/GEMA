from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.views import View

from accounts.mixins import OperacionRequiredMixin
from core.exceptions import DomainException
from matafuegos.models import Matafuegos, NotificacionVencimiento
from matafuegos.services import crear_o_reutilizar_pendiente, marcar_enviado, marcar_error, preparar_notificacion
from matafuegos.views.list import _redirect_back


class MatafuegosNotificarView(OperacionRequiredMixin, View):
    """Confirmar el modal de Notificar: crea (o reutiliza) la notificación
    PENDIENTE y redirige de vuelta abriendo el enlace `wa.me` en una
    pestaña nueva. GEMA nunca hace clic en "Enviar" por el usuario -- eso
    queda en abrir la conversación con el mensaje ya cargado."""

    def post(self, request, pk):
        matafuego = get_object_or_404(Matafuegos, pk=pk, company=request.user.company)
        try:
            preview = preparar_notificacion(matafuego)
        except DomainException as exc:
            messages.error(request, str(exc))
            return _redirect_back(request)
        crear_o_reutilizar_pendiente(matafuego, preview)
        request.session['abrir_whatsapp'] = preview.link_whatsapp
        return _redirect_back(request)


class NotificacionMarcarEnviadaView(OperacionRequiredMixin, View):
    """El usuario volvió de WhatsApp y confirma que sí lo envió: recién acá
    la notificación pasa a NOTIFICADA (el único estado que cuenta como
    "Notificado")."""

    def post(self, request, pk):
        notificacion = get_object_or_404(
            NotificacionVencimiento,
            pk=pk,
            matafuego__company=request.user.company,
            estado_envio=NotificacionVencimiento.ESTADO_PENDIENTE,
        )
        marcar_enviado(notificacion)
        messages.success(request, 'Notificación confirmada como enviada.')
        return _redirect_back(request, default='matafuegos:list')


class NotificacionMarcarErrorView(OperacionRequiredMixin, View):
    """El usuario volvió de WhatsApp y el envío no se concretó (número
    equivocado, cerró sin mandar, etc.): cierra el intento como ERROR, sin
    que cuente como notificado. Un reintento posterior crea un registro
    nuevo."""

    def post(self, request, pk):
        notificacion = get_object_or_404(
            NotificacionVencimiento,
            pk=pk,
            matafuego__company=request.user.company,
            estado_envio=NotificacionVencimiento.ESTADO_PENDIENTE,
        )
        observacion = request.POST.get('observacion', '')
        marcar_error(notificacion, observacion=observacion)
        messages.warning(request, 'Intento de notificación cerrado como error.')
        return _redirect_back(request, default='matafuegos:list')
