"""Subclases triviales de los forms de auth nativos de Django, solo para
sumarles las clases de Bootstrap del template Lexa (ver core.forms)."""

from django.contrib.auth.forms import (
    AdminPasswordChangeForm,
    AuthenticationForm,
    PasswordResetForm,
    SetPasswordForm,
)

from core.forms import BootstrapFieldsMixin


class StyledAuthenticationForm(BootstrapFieldsMixin, AuthenticationForm):
    """Suma los placeholders que usa el nuevo diseño del login (ver
    accounts/templates/accounts/login.html): los <label> de arriba se
    reemplazaron por texto dentro del input, así que el placeholder pasa
    a ser el único lugar donde se indica qué va en cada campo."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs['placeholder'] = 'Usuario'
        self.fields['password'].widget.attrs['placeholder'] = 'Contraseña'


class StyledPasswordResetForm(BootstrapFieldsMixin, PasswordResetForm):
    pass


class StyledSetPasswordForm(BootstrapFieldsMixin, SetPasswordForm):
    pass


class StyledAdminPasswordChangeForm(BootstrapFieldsMixin, AdminPasswordChangeForm):
    pass
