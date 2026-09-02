"""Subclases triviales de los forms de auth nativos de Django, solo para
sumarles las clases de Bootstrap del template Lexa (ver formutils.mixins).
Usadas exclusivamente por el portal público; el admin de Django sigue
usando los forms originales sin tocar."""

from django.contrib.auth.forms import (
    AdminPasswordChangeForm,
    AuthenticationForm,
    PasswordResetForm,
    SetPasswordForm,
)

from formutils.mixins import BootstrapFieldsMixin


class StyledAuthenticationForm(BootstrapFieldsMixin, AuthenticationForm):
    pass


class StyledPasswordResetForm(BootstrapFieldsMixin, PasswordResetForm):
    pass


class StyledSetPasswordForm(BootstrapFieldsMixin, SetPasswordForm):
    pass


class StyledAdminPasswordChangeForm(BootstrapFieldsMixin, AdminPasswordChangeForm):
    pass
