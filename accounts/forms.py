from django import forms

from formutils.mixins import BootstrapFieldsMixin
from .models import Role, User


class UserInviteForm(BootstrapFieldsMixin, forms.ModelForm):
    role = forms.ChoiceField(
        label='Rol',
        choices=[(Role.ADMIN_EMPRESA, 'Admin de compañía'), (Role.OPERADOR, 'Operador'), (Role.CLIENTE_FINAL, 'Cliente final')],
    )

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'role', 'cliente']

    def __init__(self, *args, company=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.company = company
        self.instance.company = company
        self.fields['cliente'].queryset = self.fields['cliente'].queryset.filter(company=company)
        self.fields['cliente'].required = False
        self.fields['email'].required = True

    def clean(self):
        cleaned_data = super().clean()
        role = cleaned_data.get('role')
        cliente = cleaned_data.get('cliente')
        if role == Role.CLIENTE_FINAL and not cliente:
            self.add_error('cliente', 'Debe indicar el cliente asociado para el rol Cliente final.')
        if role != Role.CLIENTE_FINAL and cliente:
            self.add_error('cliente', 'Solo los usuarios Cliente final pueden tener un cliente asociado.')
        return cleaned_data


class UserRoleUpdateForm(BootstrapFieldsMixin, forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'role', 'cliente']

    def __init__(self, *args, company=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.company = company
        self.fields['cliente'].queryset = self.fields['cliente'].queryset.filter(company=company)
        self.fields['cliente'].required = False

    def clean(self):
        cleaned_data = super().clean()
        role = cleaned_data.get('role')
        cliente = cleaned_data.get('cliente')
        if role == Role.CLIENTE_FINAL and not cliente:
            self.add_error('cliente', 'Debe indicar el cliente asociado para el rol Cliente final.')
        if role != Role.CLIENTE_FINAL and cliente:
            self.add_error('cliente', 'Solo los usuarios Cliente final pueden tener un cliente asociado.')
        return cleaned_data
