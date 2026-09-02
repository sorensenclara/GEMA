
from django import forms
from dal import autocomplete
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from django.forms import inlineformset_factory

from formutils.mixins import BootstrapFieldsMixin
from cliente.models import Cliente
from matafuegos.models import Matafuegos
from .models import Tarea, Ordenes_de_trabajo, TareaOrden



class OrdenesTrabajoAdminForm(forms.ModelForm):

    cliente = forms.ModelChoiceField(
        queryset=Cliente.objects.all(),
        widget=autocomplete.ModelSelect2(url='clientes-autocomplete',

    ))

    vencido = False
    matafuegos = forms.ModelChoiceField(
        queryset= Matafuegos.objects.all(),
        widget=autocomplete.ModelSelect2(url='matafuegos-autocomplete',
                                        forward=('cliente','vencido')
    ))


class TareaForm(BootstrapFieldsMixin, forms.ModelForm):
    class Meta:
        model = Tarea
        fields = ['nombre', 'precio', 'es_recarga']

    def __init__(self, *args, company=None, **kwargs):
        super().__init__(*args, **kwargs)
        if company is not None:
            self.instance.company = company


class MatafuegosPorClienteSelect(forms.Select):
    """<select> de matafuegos con un data-cliente por <option>, para poder
    filtrarlo con JS del lado del cliente según el cliente elegido (en el
    portal no hay jQuery/Select2 disponible como en el admin de Django, así
    que la lista completa de matafuegos de la compañía viaja igual en el
    HTML y el filtrado es puramente visual)."""

    def create_option(self, name, value, label, selected, index, subindex=None, attrs=None):
        option = super().create_option(name, value, label, selected, index, subindex=subindex, attrs=attrs)
        pk = value.value if hasattr(value, 'value') else value
        if pk:
            cliente_id = self.matafuego_cliente_ids.get(str(pk))
            if cliente_id is not None:
                option['attrs']['data-cliente'] = str(cliente_id)
        return option


class OrdenTrabajoForm(BootstrapFieldsMixin, forms.ModelForm):
    class Meta:
        model = Ordenes_de_trabajo
        fields = ['cliente', 'matafuegos', 'fecha_inicio', 'fecha_entrega', 'fecha_cierre', 'estado', 'notas']
        widgets = {
            'fecha_inicio': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
            'fecha_entrega': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
            'fecha_cierre': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
        }

    def __init__(self, *args, company=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.company = company
        if company is not None:
            self.instance.company = company
            self.fields['cliente'].queryset = Cliente.objects.filter(company=company)
            matafuegos_qs = Matafuegos.objects.filter(company=company).select_related('cliente')
            # BootstrapFieldsMixin ya corrió en super().__init__(); este widget
            # se crea después, así que necesita su clase seteada a mano.
            widget = MatafuegosPorClienteSelect(attrs={'class': 'form-select'})
            widget.matafuego_cliente_ids = {str(m.pk): m.cliente_id for m in matafuegos_qs}
            self.fields['matafuegos'].widget = widget
            self.fields['matafuegos'].queryset = matafuegos_qs


class TareaOrdenInlineForm(BootstrapFieldsMixin, forms.ModelForm):
    class Meta:
        model = TareaOrden
        fields = ['tarea', 'cant_cargada', 'precioAj']

    def __init__(self, *args, company=None, **kwargs):
        super().__init__(*args, **kwargs)
        if company is not None:
            self.fields['tarea'].queryset = Tarea.objects.filter(company=company)


def get_tarea_orden_formset_class():
    return inlineformset_factory(
        Ordenes_de_trabajo, TareaOrden,
        form=TareaOrdenInlineForm,
        fields=['tarea', 'cant_cargada', 'precioAj'],
        extra=1, can_delete=True,
    )
