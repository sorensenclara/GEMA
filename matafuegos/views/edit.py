from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView

from accounts.mixins import OperacionRequiredMixin
from matafuegos.forms import MatafuegosForm
from matafuegos.models import Matafuegos


class MatafuegosCreateView(OperacionRequiredMixin, CreateView):
    active_section = 'matafuegos'
    form_class = MatafuegosForm
    template_name = 'matafuegos/matafuegos_form.html'
    success_url = reverse_lazy('matafuegos:list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['company'] = self.request.user.company
        return kwargs

    def form_valid(self, form):
        messages.success(self.request, f'Matafuego N° {form.instance.numero} creado.')
        return super().form_valid(form)


class MatafuegosUpdateView(OperacionRequiredMixin, UpdateView):
    active_section = 'matafuegos'
    form_class = MatafuegosForm
    template_name = 'matafuegos/matafuegos_form.html'
    success_url = reverse_lazy('matafuegos:list')

    def get_queryset(self):
        return Matafuegos.objects.filter(company=self.request.user.company)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['company'] = self.request.user.company
        return kwargs

    def form_valid(self, form):
        messages.success(self.request, f'Matafuego N° {form.instance.numero} actualizado.')
        return super().form_valid(form)
