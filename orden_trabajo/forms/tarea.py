from django import forms

from core.forms import BootstrapFieldsMixin
from orden_trabajo.models import Tarea


class TareaForm(BootstrapFieldsMixin, forms.ModelForm):
    class Meta:
        model = Tarea
        fields = ['nombre', 'precio', 'es_recarga']

    def __init__(self, *args, company=None, **kwargs):
        super().__init__(*args, **kwargs)
        if company is not None:
            self.instance.company = company
