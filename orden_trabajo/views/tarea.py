from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, UpdateView

from accounts.mixins import OperacionRequiredMixin
from orden_trabajo.forms import TareaForm
from orden_trabajo.selectors import list_tareas


class TareaListView(OperacionRequiredMixin, ListView):
    active_section = 'tareas'
    template_name = 'orden_trabajo/tarea_list.html'
    context_object_name = 'tareas'

    def get_queryset(self):
        return list_tareas(self.request.user.company)


class TareaCreateView(OperacionRequiredMixin, CreateView):
    active_section = 'tareas'
    form_class = TareaForm
    template_name = 'orden_trabajo/tarea_form.html'
    success_url = reverse_lazy('orden_trabajo:tarea-list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['company'] = self.request.user.company
        return kwargs

    def form_valid(self, form):
        messages.success(self.request, f'Tarea "{form.instance.nombre}" creada.')
        return super().form_valid(form)


class TareaUpdateView(OperacionRequiredMixin, UpdateView):
    active_section = 'tareas'
    form_class = TareaForm
    template_name = 'orden_trabajo/tarea_form.html'
    success_url = reverse_lazy('orden_trabajo:tarea-list')

    def get_queryset(self):
        return list_tareas(self.request.user.company)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['company'] = self.request.user.company
        return kwargs

    def form_valid(self, form):
        messages.success(self.request, f'Tarea "{form.instance.nombre}" actualizada.')
        return super().form_valid(form)
