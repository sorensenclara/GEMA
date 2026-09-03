from dal import autocomplete
from django import forms

from cliente.models import Cliente
from matafuegos.models import Matafuegos


class OrdenesTrabajoAdminForm(forms.ModelForm):
    cliente = forms.ModelChoiceField(
        queryset=Cliente.objects.all(),
        widget=autocomplete.ModelSelect2(url='clientes-autocomplete'),
    )

    vencido = False
    matafuegos = forms.ModelChoiceField(
        queryset=Matafuegos.objects.all(),
        widget=autocomplete.ModelSelect2(url='matafuegos-autocomplete', forward=('cliente', 'vencido')),
    )
