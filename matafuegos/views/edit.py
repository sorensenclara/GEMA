from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView

from accounts.mixins import OperacionRequiredMixin
from core.exceptions import DomainException
from matafuegos.forms import MatafuegosForm
from matafuegos.models import Matafuegos
from matafuegos.selectors import notificacion_vigente
from matafuegos.services import preparar_notificacion


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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        matafuego = self.object
        context['notificacion_actual'] = notificacion_vigente(matafuego)
        try:
            context['notificacion_preview'] = preparar_notificacion(matafuego)
        except DomainException as exc:
            context['notificacion_preview'] = None
            context['notificacion_error'] = str(exc)
        # Flag de una sola lectura: lo dejó MatafuegosNotificarView en la
        # sesión para que esta página, al recargarse, abra WhatsApp en una
        # pestaña nueva -- nunca se guarda el enlace en la URL.
        context['abrir_whatsapp'] = self.request.session.pop('abrir_whatsapp', None)
        return context

    def form_valid(self, form):
        messages.success(self.request, f'Matafuego N° {form.instance.numero} actualizado.')
        return super().form_valid(form)
