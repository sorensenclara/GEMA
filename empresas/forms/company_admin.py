from django import forms
from django.contrib.auth import get_user_model

from empresas.models import Company

User = get_user_model()


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

    def clean_admin_username(self):
        username = self.cleaned_data['admin_username']
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError(
                'Ya existe un usuario con este nombre de usuario.'
            )
        return username


class CompanyRangesForm(forms.ModelForm):
    class Meta:
        model = Company
        fields = [
            'nombre', 'is_active', 'numero_recargador',
            'veh_prefijo', 'veh_inicio', 'veh_fin', 'veh_actual',
            'dom_prefijo', 'dom_inicio', 'dom_fin', 'dom_actual',
        ]
