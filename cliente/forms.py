from django import forms
from .models import Cliente
from django.core.validators import URLValidator
from formutils.mixins import BootstrapFieldsMixin


class ClienteForm(BootstrapFieldsMixin, forms.ModelForm):
    class Meta:
        model = Cliente
        fields = ['codigo', 'nombre', 'cuit_cuil', 'contacto', 'direccion', 'telefono', 'email', 'web', 'tipo', 'estado']

    def __init__(self, *args, company=None, **kwargs):
        super().__init__(*args, **kwargs)
        if company is not None:
            self.instance.company = company


class ControlWebForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = '__all__'

    def clean(self):
        validator = URLValidator(verify_exists=True)
        try:
            validator(self.cleaned_data.get('web'))
        except:
            raise forms.ValidationError('Debe especificar una web valida')
