from django import forms

from core.forms import BootstrapFieldsMixin
from matafuegos.models import Matafuegos


class MatafuegosForm(BootstrapFieldsMixin, forms.ModelForm):
    class Meta:
        model = Matafuegos
        fields = [
            'numero', 'numeroInterno', 'cliente', 'patente', 'direccion',
            'localizacion', 'numero_localizacion', 'marca', 'tipo', 'categoria',
            'fecha_fabricacion', 'fecha_carga', 'fecha_ph', 'numero_dps',
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
        if self.instance.pk:
            # El numero de DPS solo se carga a mano al crear el matafuego;
            # luego se completa automaticamente desde la orden de trabajo.
            self.fields['numero_dps'].widget.attrs['readonly'] = True

    def clean_numero_dps(self):
        if self.instance.pk:
            return self.instance.numero_dps
        return self.cleaned_data.get('numero_dps')
