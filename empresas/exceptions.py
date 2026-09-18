from core.exceptions import DomainException


class RangoDpsAgotadoException(DomainException):
    """El rango de numeración DPS configurado para la serie (veh/dom) de la
    compañía se agotó -- incrementar_dps() lo alcanzaría o superaría."""


class NumeracionDpsNoConfiguradaException(DomainException):
    """Faltan definir el prefijo y/o el número final de la serie (veh/dom)
    en la ficha de la compañía -- incrementar_dps() no puede emitir sin eso."""
