from core.exceptions import DomainException


class SinMatafuegosParaAlertaException(DomainException):
    """No hay matafuegos con vencimiento en el rango de fechas pedido para la alerta."""


class SinMatafuegosParaInformeException(DomainException):
    """No hay matafuegos con vencimiento próximo para el informe."""


class RangoDeFechasInvalidoException(DomainException):
    """La fecha de fin del rango es anterior a la fecha de inicio."""


class ClienteSinWhatsAppException(DomainException):
    """El cliente del matafuego no tiene un teléfono normalizado y válido
    para armar un enlace de WhatsApp."""


class MatafuegoSinVencimientoException(DomainException):
    """El matafuego no tiene ningún vencimiento (carga o PH) próximo -- no
    hay nada que notificar."""
