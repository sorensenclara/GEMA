from core.exceptions import DomainException


class CategoriaOrdenInvalidaException(DomainException):
    """La categoría del matafuego de la orden no corresponde a la oblea
    solicitada (vehicular/domiciliaria)."""


class OrdenNoFinalizadaException(DomainException):
    """No se puede emitir la oblea de una orden que no está finalizada."""


class OrdenSinFechaCierreException(DomainException):
    """No se puede emitir la oblea de una orden sin fecha de cierre."""


class OrdenSinTareaDeRecargaException(DomainException):
    """No se puede emitir la oblea de una orden que no incluye ninguna tarea
    de recarga."""


class DebeSeleccionarUnaOrdenException(DomainException):
    """La acción requiere seleccionar exactamente una orden de trabajo."""


class SinOrdenesParaFacturarException(DomainException):
    """No hay órdenes de trabajo para incluir en el informe de facturación."""


class TransicionDeEstadoInvalidaException(DomainException):
    """La orden no está en un estado desde el que se pueda aplicar la acción
    pedida (ej. finalizar una orden que no está en proceso)."""


class RangoDeFechasInvalidoException(DomainException):
    """La fecha de fin del rango es anterior a la de inicio."""


class SinRecargasParaInformeException(DomainException):
    """No hay matafuegos recargados (con oblea DPS emitida) entre las fechas
    indicadas."""


class SinHistorialParaInformeException(DomainException):
    """El matafuego no tiene ordenes de trabajo cerradas para incluir en el
    informe historico."""
