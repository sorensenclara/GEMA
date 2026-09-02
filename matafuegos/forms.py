from django import forms

from formutils.mixins import BootstrapFieldsMixin
from .models import Matafuegos


class MatafuegosForm(BootstrapFieldsMixin, forms.ModelForm):
    class Meta:
        model = Matafuegos
        fields = [
            'numero', 'numeroInterno', 'cliente', 'patente', 'direccion',
            'localizacion', 'numero_localizacion', 'marca', 'tipo', 'categoria',
            'fecha_fabricacion', 'fecha_carga', 'fecha_ph',
        ]
        widgets = {
            'fecha_fabricacion': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
            'fecha_carga': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
            'fecha_ph': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
        }

    def __init__(self, *args, company=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.company = company
        if company is not None:
            self.instance.company = company
            self.fields['cliente'].queryset = self.fields['cliente'].queryset.filter(company=company)
