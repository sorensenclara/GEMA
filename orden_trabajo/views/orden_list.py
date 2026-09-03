from django.views.generic import ListView

from accounts.mixins import OperacionRequiredMixin
from matafuegos.models import CATEGORIAS, TipoMatafuegos
from orden_trabajo.models import ESTADOS
from orden_trabajo.selectors import list_ordenes


class OrdenListView(OperacionRequiredMixin, ListView):
    active_section = 'ordenes'
    template_name = 'orden_trabajo/orden_list.html'
    context_object_name = 'ordenes'

    def get_queryset(self):
        return list_ordenes(
            self.request.user.company,
            estado=self.request.GET.get('estado'),
            tipo_matafuego=self.request.GET.get('tipo_matafuego'),
            categoria_matafuego=self.request.GET.get('categoria_matafuego'),
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['estados'] = ESTADOS
        context['tipos_matafuego'] = TipoMatafuegos.objects.order_by('tipo')
        context['categorias_matafuego'] = CATEGORIAS
        return context
