from core.exceptions import DomainException


class RangoDpsAgotadoException(DomainException):
    """El rango de numeración DPS configurado para la serie (veh/dom) de la
    compañía se agotó -- incrementar_dps() lo alcanzaría o superaría."""
