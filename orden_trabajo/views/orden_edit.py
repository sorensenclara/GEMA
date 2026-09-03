from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView

from accounts.mixins import OperacionRequiredMixin
from orden_trabajo.forms import OrdenTrabajoForm, get_tarea_orden_formset_class
from orden_trabajo.models import Ordenes_de_trabajo
from orden_trabajo.services import recalcular_monto_total


class OrdenFormMixin:
    def get_formset(self, instance=None, data=None):
        FormSetClass = get_tarea_orden_formset_class()
        return FormSetClass(data, instance=instance, form_kwargs={'company': self.request.user.company})

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['company'] = self.request.user.company
        return kwargs


class OrdenCreateView(OrdenFormMixin, OperacionRequiredMixin, CreateView):
    active_section = 'ordenes'
    form_class = OrdenTrabajoForm
    template_name = 'orden_trabajo/orden_form.html'
    success_url = reverse_lazy('orden_trabajo:orden-list')

    def post(self, request, *args, **kwargs):
        self.object = None
        form = self.get_form()
        form.instance.usuario = request.user.username
        formset = self.get_formset(data=request.POST)
        if form.is_valid() and formset.is_valid():
            self.object = form.save()
            formset.instance = self.object
            formset.save()
            recalcular_monto_total(self.object)
            messages.success(request, f'Orden N° {self.object.id} creada.')
            return redirect(self.success_url)
        return self.render_to_response(self.get_context_data(form=form, formset=formset))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if 'formset' not in context:
            context['formset'] = self.get_formset()
        return context


class OrdenUpdateView(OrdenFormMixin, OperacionRequiredMixin, UpdateView):
    active_section = 'ordenes'
    form_class = OrdenTrabajoForm
    template_name = 'orden_trabajo/orden_form.html'
    success_url = reverse_lazy('orden_trabajo:orden-list')

    def get_queryset(self):
        return Ordenes_de_trabajo.objects.filter(company=self.request.user.company)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()
        formset = self.get_formset(instance=self.object, data=request.POST)
        if form.is_valid() and formset.is_valid():
            self.object = form.save()
            formset.save()
            recalcular_monto_total(self.object)
            messages.success(request, f'Orden N° {self.object.id} actualizada.')
            return redirect(self.success_url)
        return self.render_to_response(self.get_context_data(form=form, formset=formset))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if 'formset' not in context:
            context['formset'] = self.get_formset(instance=self.object)
        return context
