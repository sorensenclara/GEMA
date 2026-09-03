from core.exceptions import DomainException


class SinMatafuegosParaAlertaException(DomainException):
    """No hay matafuegos con vencimiento en el rango de fechas pedido para la alerta."""


class SinMatafuegosParaInformeException(DomainException):
    """No hay matafuegos con vencimiento próximo para el informe."""


class RangoDeFechasInvalidoException(DomainException):
    """La fecha de fin del rango es anterior a la fecha de inicio."""
