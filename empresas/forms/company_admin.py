from django import forms

from empresas.models import Company


class CompanyCreateForm(forms.ModelForm):
    admin_username = forms.CharField(label='Usuario del admin de compañía')
    admin_email = forms.EmailField(label='Email del admin de compañía')

    class Meta:
        model = Company
        fields = [
            'nombre', 'logo', 'numero_recargador',
            'veh_prefijo', 'veh_inicio', 'veh_fin', 'veh_actual',
            'dom_prefijo', 'dom_inicio', 'dom_fin', 'dom_actual',
        ]


class CompanyRangesForm(forms.ModelForm):
    class Meta:
        model = Company
        fields = [
            'nombre', 'is_active', 'numero_recargador',
            'veh_prefijo', 'veh_inicio', 'veh_fin', 'veh_actual',
            'dom_prefijo', 'dom_inicio', 'dom_fin', 'dom_actual',
        ]
