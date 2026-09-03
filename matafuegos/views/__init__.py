from .autocomplete import MatafuegosAutoComplete
from .edit import MatafuegosCreateView, MatafuegosUpdateView
from .list import (
    MatafuegosActivarView,
    MatafuegosEliminarView,
    MatafuegosListadoInformeView,
    MatafuegosListView,
)
from .mis_matafuegos import MisMatafuegosDetailView, MisMatafuegosListView
from .vencimientos import MatafuegosProximosVencimientosView, MatafuegosVencimientosView

__all__ = [
    'MatafuegosListView',
    'MatafuegosListadoInformeView',
    'MatafuegosEliminarView',
    'MatafuegosActivarView',
    'MatafuegosCreateView',
    'MatafuegosUpdateView',
    'MatafuegosVencimientosView',
    'MatafuegosProximosVencimientosView',
    'MisMatafuegosListView',
    'MisMatafuegosDetailView',
    'MatafuegosAutoComplete',
]
