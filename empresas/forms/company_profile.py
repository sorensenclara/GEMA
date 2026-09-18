from django import forms

from core.forms import BootstrapFieldsMixin
from empresas.models import Company


class CompanyProfileForm(BootstrapFieldsMixin, forms.ModelForm):
    """Edición del perfil de la compañía por su propio Admin de compañía:
    datos generales, numeración de DPS y SMTP. La activación/desactivación
    de la compañía (is_active) sigue siendo superadmin-only (ver
    CompanyRangesForm), para evitar que un admin de empresa se autobloquee."""

    class Meta:
        model = Company
        fields = [
            'nombre', 'logo', 'numero_recargador',
            'veh_prefijo', 'veh_inicio', 'veh_fin', 'veh_actual',
            'dom_prefijo', 'dom_inicio', 'dom_fin', 'dom_actual',
            'smtp_email', 'smtp_password',
        ]
