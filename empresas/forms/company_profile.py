from django import forms

from core.forms import BootstrapFieldsMixin
from empresas.models import Company


class CompanyProfileForm(BootstrapFieldsMixin, forms.ModelForm):
    """Edición del perfil de la compañía por su propio Admin de compañía:
    solo nombre/logo/SMTP. Los rangos de numeración DPS son superadmin-only
    (ver CompanyRangesForm)."""

    class Meta:
        model = Company
        fields = ['nombre', 'logo', 'smtp_email', 'smtp_password']
