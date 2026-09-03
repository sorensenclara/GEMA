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
    pass


class StyledPasswordResetForm(BootstrapFieldsMixin, PasswordResetForm):
    pass


class StyledSetPasswordForm(BootstrapFieldsMixin, SetPasswordForm):
    pass


class StyledAdminPasswordChangeForm(BootstrapFieldsMixin, AdminPasswordChangeForm):
    pass
