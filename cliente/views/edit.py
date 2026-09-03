from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView

from accounts.mixins import OperacionRequiredMixin
from cliente.forms import ClienteForm
from cliente.models import Cliente
from matafuegos.models import Matafuegos
from orden_trabajo.models import Ordenes_de_trabajo


class ClienteCreateView(OperacionRequiredMixin, CreateView):
    active_section = 'clientes'
    form_class = ClienteForm
    template_name = 'cliente/cliente_form.html'
    success_url = reverse_lazy('cliente:list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['company'] = self.request.user.company
        return kwargs

    def form_valid(self, form):
        messages.success(self.request, f'Cliente "{form.instance.nombre}" creado.')
        return super().form_valid(form)


class ClienteUpdateView(OperacionRequiredMixin, UpdateView):
    active_section = 'clientes'
    form_class = ClienteForm
    template_name = 'cliente/cliente_form.html'
    success_url = reverse_lazy('cliente:list')

    def get_queryset(self):
        return Cliente.objects.filter(company=self.request.user.company)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['company'] = self.request.user.company
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['matafuegos_cliente'] = Matafuegos.objects.filter(cliente=self.object).select_related('tipo').order_by('numero')
        context['ordenes_cliente'] = Ordenes_de_trabajo.objects.filter(cliente=self.object).select_related('matafuegos').order_by('-fecha_creacion')
        return context

    def form_valid(self, form):
        messages.success(self.request, f'Cliente "{form.instance.nombre}" actualizado.')
        return super().form_valid(form)
