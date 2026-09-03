from core.exceptions import DomainException


class NoPuedeDesactivarsePropioUsuarioException(DomainException):
    """Un usuario no puede desactivar su propia cuenta: sin esto, un Admin de
    compañía con acceso a la gestión de usuarios podría bloquearse a sí mismo
    sin que nadie más de su compañía pueda reactivarlo."""
