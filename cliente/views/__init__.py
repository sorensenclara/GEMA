from .actions import ClienteEnviarInformeView, ClienteInformeView, ClienteToggleActiveView
from .autocomplete import ClienteAutoComplete
from .edit import ClienteCreateView, ClienteUpdateView
from .geocoding import ClienteUbicacionBuscarView
from .list import ClienteListadoInformeView, ClienteListView

__all__ = [
    'ClienteListView',
    'ClienteListadoInformeView',
    'ClienteCreateView',
    'ClienteUpdateView',
    'ClienteToggleActiveView',
    'ClienteInformeView',
    'ClienteEnviarInformeView',
    'ClienteAutoComplete',
    'ClienteUbicacionBuscarView',
]
