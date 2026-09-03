from core.exceptions import DomainException


class DebeSeleccionarUnSoloClienteException(DomainException):
    """Una acción que opera sobre un único cliente (informe, envío por email)
    fue invocada con más de un cliente seleccionado."""


class ClienteSinEmailException(DomainException):
    """El cliente no tiene un email cargado -- no se le puede enviar el informe."""


class SmtpNoConfiguradoException(DomainException):
    """La compañía no tiene email/contraseña SMTP configurados para el envío
    de informes a clientes."""


class CredencialesSmtpInvalidasException(DomainException):
    """El servidor SMTP rechazó las credenciales configuradas en la compañía."""
