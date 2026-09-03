from core.exceptions import DomainException


class CantidadOrdenesImparException(DomainException):
    """La oblea DPS se emite de a pares de órdenes; la cantidad seleccionada
    no es múltiplo de dos."""


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
