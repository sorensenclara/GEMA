from django import forms

from cliente.models import Cliente
from core.forms import BootstrapFieldsMixin


class ClienteForm(BootstrapFieldsMixin, forms.ModelForm):
    class Meta:
        model = Cliente
        fields = ['codigo', 'nombre', 'cuit_cuil', 'contacto', 'direccion', 'telefono', 'email', 'web', 'tipo', 'estado']

    def __init__(self, *args, company=None, **kwargs):
        super().__init__(*args, **kwargs)
        if company is not None:
            self.instance.company = company
