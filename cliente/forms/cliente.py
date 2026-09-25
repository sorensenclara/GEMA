from django import forms

from cliente.models import Cliente
from core.forms import BootstrapFieldsMixin
from core.services import obtener_seleccion


class ClienteForm(BootstrapFieldsMixin, forms.ModelForm):
    """El campo `direccion` sigue siendo el único campo de ubicación visible
    y editable (ver cliente_form.html + core/static/core/js/ubicacion-buscador.js).
    Los campos geo_* del modelo (localidad, provincia, codigo_postal, pais,
    geo_referencia_externa, geo_provider, geo_status) NO están en Meta.fields
    a propósito: no son datos que el usuario tipee, se calculan acá en
    clean()/save() a partir de lo que devolvió el buscador de ubicaciones.

    El navegador nunca manda esos datos estructurados directamente: solo
    manda `geo_seleccion_token` (una referencia opaca a una búsqueda
    reciente cacheada en el servidor, ver core/services/geocoding.py) y
    `geo_tocado` (si el usuario llegó a interactuar con el buscador). El
    servidor es la única autoridad sobre qué termina guardado -- nadie
    puede escribir a mano latitud/localidad/provincia/etc. porque esos
    campos no existen como inputs editables en ningún lado.
    """

    geo_seleccion_token = forms.CharField(required=False, widget=forms.HiddenInput)
    geo_tocado = forms.CharField(required=False, widget=forms.HiddenInput)

    class Meta:
        model = Cliente
        fields = ['codigo', 'nombre', 'cuit_cuil', 'contacto', 'direccion', 'telefono', 'email', 'web', 'tipo', 'estado']

    def __init__(self, *args, company=None, **kwargs):
        super().__init__(*args, **kwargs)
        if company is not None:
            self.instance.company = company

    def clean(self):
        cleaned_data = super().clean()
        tocado = cleaned_data.get('geo_tocado') == '1'
        token = cleaned_data.get('geo_seleccion_token')

        if not tocado:
            # El usuario no interactuó con el buscador de ubicación en esta
            # edición: se conserva lo que el cliente ya tenía (o, si es un
            # cliente nuevo, se resuelve como carga manual en save()).
            self._geo_resultado = None
            return cleaned_data

        seleccion = obtener_seleccion(token) if token else None
        if seleccion is not None:
            self._geo_resultado = {
                'direccion': seleccion['direccion'],
                'localidad': seleccion['localidad'],
                'provincia': seleccion['provincia'],
                'codigo_postal': seleccion['codigo_postal'],
                'pais': seleccion['pais'],
                'geo_referencia_externa': seleccion['geo_referencia_externa'],
                'geo_provider': 'nominatim',
                'geo_status': 'georreferenciado',
            }
        else:
            # Token vencido/inexistente, o carga manual explícita: se
            # guarda el texto que el usuario tipeó tal cual, sin inventar
            # localidad/provincia/código postal/país.
            self._geo_resultado = {
                'direccion': cleaned_data.get('direccion') or '',
                'localidad': '',
                'provincia': '',
                'codigo_postal': '',
                'pais': '',
                'geo_referencia_externa': '',
                'geo_provider': '',
                'geo_status': 'manual_no_encontrado',
            }
        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        if self._geo_resultado is not None:
            for campo, valor in self._geo_resultado.items():
                setattr(instance, campo, valor)
        elif not instance.pk:
            # Cliente nuevo guardado sin haber tocado el buscador (por
            # ejemplo con JS deshabilitado): la creación del cliente nunca
            # debe quedar bloqueada por esto, se guarda como carga manual
            # con el texto que haya quedado en el campo Dirección.
            instance.geo_status = 'manual_no_encontrado'
        if commit:
            instance.save()
        return instance
