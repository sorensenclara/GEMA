from io import BytesIO

from django.contrib import messages
from django.http import FileResponse
from django.shortcuts import get_object_or_404, redirect
from django.utils.http import url_has_allowed_host_and_scheme
from django.views import View
from django.views.generic import ListView

from accounts.mixins import OperacionRequiredMixin
from matafuegos.models import ESTADOS, Matafuegos, TipoMatafuegos
from matafuegos.selectors import list_matafuegos
from matafuegos.services import activar_matafuego, eliminar_matafuego, generar_listado_matafuegos


def _filtros_get(request):
    return {
        'q': request.GET.get('q'),
        'tipo': request.GET.get('tipo'),
        'estado': request.GET.get('estado'),
        'vencido': request.GET.get('vencido'),
    }


def _redirect_back(request, default='matafuegos:list'):
    """Vuelve a la página desde la que se disparó la acción (grilla de
    Matafuegos o la grilla de Matafuegos de un cliente en cliente_form.html),
    o al listado de matafuegos si no hay un referer propio válido."""
    referer = request.META.get('HTTP_REFERER')
    if referer and url_has_allowed_host_and_scheme(referer, allowed_hosts={request.get_host()}, require_https=request.is_secure()):
        return redirect(referer)
    return redirect(default)


class MatafuegosListView(OperacionRequiredMixin, ListView):
    active_section = 'matafuegos'
    template_name = 'matafuegos/matafuegos_list.html'
    context_object_name = 'matafuegos'

    def get_queryset(self):
        return list_matafuegos(self.request.user.company, **_filtros_get(self.request))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tipos'] = TipoMatafuegos.objects.order_by('tipo')
        context['estados'] = ESTADOS
        return context


class MatafuegosListadoInformeView(OperacionRequiredMixin, View):
    def get(self, request):
        qs = list_matafuegos(request.user.company, **_filtros_get(request))
        pdf_bytes = generar_listado_matafuegos(qs)
        return FileResponse(BytesIO(pdf_bytes), as_attachment=True, filename='listado_matafuegos.pdf')


class MatafuegosEliminarView(OperacionRequiredMixin, View):
    def post(self, request, pk):
        matafuego = get_object_or_404(Matafuegos, pk=pk, company=request.user.company)
        numero = matafuego.numero
        eliminado = eliminar_matafuego(matafuego)
        if eliminado:
            messages.success(request, f'Matafuego N° {numero} eliminado.')
        else:
            messages.success(request, f'Matafuego N° {numero} dado de baja (tiene órdenes de trabajo asociadas).')
        return _redirect_back(request)


class MatafuegosActivarView(OperacionRequiredMixin, View):
    def post(self, request, pk):
        matafuego = get_object_or_404(Matafuegos, pk=pk, company=request.user.company)
        activar_matafuego(matafuego)
        messages.success(request, f'Matafuego N° {matafuego.numero} activado.')
        return _redirect_back(request)
