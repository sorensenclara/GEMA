from django import forms

from formutils.mixins import BootstrapFieldsMixin
from .models import Company


class CompanyProfileForm(BootstrapFieldsMixin, forms.ModelForm):
    """Edición del perfil de la compañía por su propio Admin de compañía:
    solo nombre/logo/SMTP. Los rangos de numeración DPS son superadmin-only
    (ver CompanyRangesForm, en el panel)."""

    class Meta:
        model = Company
        fields = ['nombre', 'logo', 'smtp_email', 'smtp_password']


class CompanyCreateForm(forms.ModelForm):
    admin_username = forms.CharField(label='Usuario del admin de compañía')
    admin_email = forms.EmailField(label='Email del admin de compañía')

    class Meta:
        model = Company
        fields = [
            'nombre', 'logo',
            'veh_prefijo', 'veh_inicio', 'veh_fin', 'veh_actual',
            'dom_prefijo', 'dom_inicio', 'dom_fin', 'dom_actual',
        ]


class CompanyRangesForm(forms.ModelForm):
    class Meta:
        model = Company
        fields = [
            'nombre', 'is_active',
            'veh_prefijo', 'veh_inicio', 'veh_fin', 'veh_actual',
            'dom_prefijo', 'dom_inicio', 'dom_fin', 'dom_actual',
        ]
