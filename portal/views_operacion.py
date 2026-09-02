from datetime import date, timedelta
from io import BytesIO

from django.contrib import messages
from django.db.models import Q
from django.http import FileResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import ListView, CreateView, UpdateView

from accounts.mixins import OperacionRequiredMixin
from cliente.admin import generarInformeCliente, generarListadoClientes, send_email as accion_enviar_informe_email
from cliente.forms import ClienteForm
from cliente.models import Cliente
from matafuegos.admin import emitirAlerta, generarListadoMatafuegos
from matafuegos.forms import MatafuegosForm
from matafuegos.models import Matafuegos
from orden_trabajo.admin import (
    InformeFacturacion as accion_informe_facturacion,
    InformeFacturacion_ultimaSemana,
    emitirInformeDPSFijo as accion_oblea_domiciliaria,
    emitirInformeOrden,
    emitirInformeVehicular as accion_oblea_vehicular,
)
from orden_trabajo.forms import OrdenTrabajoForm, TareaForm, get_tarea_orden_formset_class
from orden_trabajo.models import Ordenes_de_trabajo, Tarea


# ---------------------------------------------------------------- Cliente --

class ClienteListView(OperacionRequiredMixin, ListView):
    active_section = 'clientes'
    template_name = 'portal/cliente_list.html'
    context_object_name = 'clientes'

    def get_queryset(self):
        qs = Cliente.objects.filter(company=self.request.user.company).order_by('nombre')
        q = self.request.GET.get('q')
        if q:
            qs = qs.filter(Q(nombre__icontains=q) | Q(codigo__icontains=q) | Q(cuit_cuil__icontains=q))
        return qs


class ClienteListadoInformeView(OperacionRequiredMixin, View):
    def get(self, request):
        qs = Cliente.objects.filter(company=request.user.company).order_by('nombre')
        q = request.GET.get('q')
        if q:
            qs = qs.filter(Q(nombre__icontains=q) | Q(codigo__icontains=q) | Q(cuit_cuil__icontains=q))
        pdf_bytes = generarListadoClientes(qs)
        return FileResponse(BytesIO(pdf_bytes), as_attachment=True, filename='listado_clientes.pdf')


class ClienteCreateView(OperacionRequiredMixin, CreateView):
    active_section = 'clientes'
    form_class = ClienteForm
    template_name = 'portal/cliente_form.html'
    success_url = reverse_lazy('portal:cliente-list')

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
    template_name = 'portal/cliente_form.html'
    success_url = reverse_lazy('portal:cliente-list')

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


class ClienteToggleActiveView(OperacionRequiredMixin, View):
    def post(self, request, pk):
        cliente = get_object_or_404(Cliente, pk=pk, company=request.user.company)
        cliente.estado = 'i' if cliente.estado == 'a' else 'a'
        cliente.save(update_fields=['estado'])
        messages.success(request, f'Cliente "{cliente.nombre}" {"activado" if cliente.estado == "a" else "desactivado"}.')
        return redirect('portal:cliente-list')


class ClienteInformeView(OperacionRequiredMixin, View):
    def get(self, request, pk):
        cliente = get_object_or_404(Cliente, pk=pk, company=request.user.company)
        pdf_bytes = generarInformeCliente(request, Cliente.objects.filter(pk=cliente.pk))
        if pdf_bytes is None:
            return redirect('portal:cliente-list')
        return FileResponse(BytesIO(pdf_bytes), as_attachment=True, filename=f'informe_{cliente.codigo}.pdf')


class ClienteEnviarInformeView(OperacionRequiredMixin, View):
    def post(self, request, pk):
        cliente = get_object_or_404(Cliente, pk=pk, company=request.user.company)
        resultado = accion_enviar_informe_email(None, request, Cliente.objects.filter(pk=cliente.pk))
        if resultado is None:
            return redirect('portal:cliente-list')
        return resultado


# -------------------------------------------------------------- Matafuegos --

class MatafuegosListView(OperacionRequiredMixin, ListView):
    active_section = 'matafuegos'
    template_name = 'portal/matafuegos_list.html'
    context_object_name = 'matafuegos'

    def get_queryset(self):
        qs = Matafuegos.objects.filter(company=self.request.user.company).select_related('cliente', 'tipo').order_by('numero')
        q = self.request.GET.get('q')
        if q:
            qs = qs.filter(Q(numero__icontains=q) | Q(cliente__nombre__icontains=q) | Q(numero_dps__icontains=q))
        return qs


class MatafuegosListadoInformeView(OperacionRequiredMixin, View):
    def get(self, request):
        qs = Matafuegos.objects.filter(company=request.user.company).select_related('cliente', 'tipo').order_by('numero')
        q = request.GET.get('q')
        if q:
            qs = qs.filter(Q(numero__icontains=q) | Q(cliente__nombre__icontains=q) | Q(numero_dps__icontains=q))
        pdf_bytes = generarListadoMatafuegos(qs)
        return FileResponse(BytesIO(pdf_bytes), as_attachment=True, filename='listado_matafuegos.pdf')


class MatafuegosCreateView(OperacionRequiredMixin, CreateView):
    active_section = 'matafuegos'
    form_class = MatafuegosForm
    template_name = 'portal/matafuegos_form.html'
    success_url = reverse_lazy('portal:matafuegos-list')

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
    template_name = 'portal/matafuegos_form.html'
    success_url = reverse_lazy('portal:matafuegos-list')

    def get_queryset(self):
        return Matafuegos.objects.filter(company=self.request.user.company)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['company'] = self.request.user.company
        return kwargs

    def form_valid(self, form):
        messages.success(self.request, f'Matafuego N° {form.instance.numero} actualizado.')
        return super().form_valid(form)


class MatafuegosVencimientosView(OperacionRequiredMixin, View):
    """Alerta de vencimientos entre dos fechas elegidas por el usuario."""

    def get(self, request):
        return render(request, 'portal/matafuegos_vencimientos.html')

    def post(self, request):
        inicio = request.POST.get('inicio')
        fin = request.POST.get('fin')
        if not inicio or not fin:
            messages.error(request, 'Especificar fecha de inicio y fin.')
            return redirect('portal:matafuegos-vencimientos')
        if inicio > fin:
            messages.error(request, 'La fecha de fin debe ser mayor a la de inicio.')
            return redirect('portal:matafuegos-vencimientos')
        qs = Matafuegos.objects.filter(
            company=request.user.company,
            fecha_proxima_carga__range=(inicio, fin),
        ).order_by('categoria', 'cliente__nombre')
        resultado = emitirAlerta(None, request, qs, inicio, fin)
        if resultado is None:
            return redirect('portal:matafuegos-vencimientos')
        return resultado


class MatafuegosProximosVencimientosView(OperacionRequiredMixin, View):
    def get(self, request):
        today = date.today()
        td = timedelta(30)
        carga = Matafuegos.objects.filter(
            company=request.user.company, fecha_proxima_carga__range=(today, today + td),
        ).order_by('categoria', 'cliente__nombre')
        ph = Matafuegos.objects.filter(
            company=request.user.company, fecha_proxima_ph__range=(today, today + td),
        ).order_by('categoria', 'cliente__nombre')
        from matafuegos.admin import MatafuegosAdmin
        admin_helper = MatafuegosAdmin(Matafuegos, None)
        resultado = admin_helper.emitirInforme(request, carga, ph)
        if resultado is None:
            return redirect('portal:matafuegos-list')
        return resultado


# --------------------------------------------------------- Tarea (catálogo) --

class TareaListView(OperacionRequiredMixin, ListView):
    active_section = 'tareas'
    template_name = 'portal/tarea_list.html'
    context_object_name = 'tareas'

    def get_queryset(self):
        return Tarea.objects.filter(company=self.request.user.company).order_by('nombre')


class TareaCreateView(OperacionRequiredMixin, CreateView):
    active_section = 'tareas'
    form_class = TareaForm
    template_name = 'portal/tarea_form.html'
    success_url = reverse_lazy('portal:tarea-list')

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
    template_name = 'portal/tarea_form.html'
    success_url = reverse_lazy('portal:tarea-list')

    def get_queryset(self):
        return Tarea.objects.filter(company=self.request.user.company)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['company'] = self.request.user.company
        return kwargs

    def form_valid(self, form):
        messages.success(self.request, f'Tarea "{form.instance.nombre}" actualizada.')
        return super().form_valid(form)


# --------------------------------------------------------- Ordenes de trabajo --

class OrdenListView(OperacionRequiredMixin, ListView):
    active_section = 'ordenes'
    template_name = 'portal/orden_list.html'
    context_object_name = 'ordenes'

    def get_queryset(self):
        qs = Ordenes_de_trabajo.objects.filter(company=self.request.user.company).select_related('cliente', 'matafuegos').order_by('-fecha_cierre', '-id')
        estado = self.request.GET.get('estado')
        if estado:
            qs = qs.filter(estado=estado)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['estados'] = Ordenes_de_trabajo._meta.get_field('estado').choices
        return context


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
    template_name = 'portal/orden_form.html'
    success_url = reverse_lazy('portal:orden-list')

    def post(self, request, *args, **kwargs):
        self.object = None
        form = self.get_form()
        form.instance.usuario = request.user.username
        formset = self.get_formset(data=request.POST)
        if form.is_valid() and formset.is_valid():
            self.object = form.save()
            formset.instance = self.object
            formset.save()
            self.object.save()  # recalcula monto_total con las tareas ya guardadas
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
    template_name = 'portal/orden_form.html'
    success_url = reverse_lazy('portal:orden-list')

    def get_queryset(self):
        return Ordenes_de_trabajo.objects.filter(company=self.request.user.company)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()
        formset = self.get_formset(instance=self.object, data=request.POST)
        if form.is_valid() and formset.is_valid():
            self.object = form.save()
            formset.save()
            self.object.save()
            messages.success(request, f'Orden N° {self.object.id} actualizada.')
            return redirect(self.success_url)
        return self.render_to_response(self.get_context_data(form=form, formset=formset))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if 'formset' not in context:
            context['formset'] = self.get_formset(instance=self.object)
        return context


class OrdenInformeView(OperacionRequiredMixin, View):
    def get(self, request, pk):
        orden = get_object_or_404(Ordenes_de_trabajo, pk=pk, company=request.user.company)
        return emitirInformeOrden(None, request, Ordenes_de_trabajo.objects.filter(pk=orden.pk))


class OrdenAccionMasivaView(OperacionRequiredMixin, View):
    """Acciones que aplican sobre varias órdenes seleccionadas por checkbox
    en el listado (oblea DPS vehicular/domiciliaria, informe de facturación)."""

    ACCIONES = {
        'oblea_vehicular': accion_oblea_vehicular,
        'oblea_domiciliaria': accion_oblea_domiciliaria,
        'informe_facturacion': accion_informe_facturacion,
    }

    def post(self, request):
        accion = request.POST.get('accion')
        func = self.ACCIONES.get(accion)
        if func is None:
            messages.error(request, 'Acción inválida.')
            return redirect('portal:orden-list')
        ids = request.POST.getlist('seleccionadas')
        if not ids:
            messages.error(request, 'Seleccioná al menos una orden.')
            return redirect('portal:orden-list')
        qs = Ordenes_de_trabajo.objects.filter(pk__in=ids, company=request.user.company)
        resultado = func(None, request, qs)
        if resultado is None:
            return redirect('portal:orden-list')
        return resultado


class OrdenInformeFacturacionUltimaSemanaView(OperacionRequiredMixin, View):
    def get(self, request):
        today = date.today()
        td = timedelta(7)
        ordenes = Ordenes_de_trabajo.objects.filter(
            company=request.user.company, estado='i', fecha_cierre__range=(today - td, today),
        ).order_by('cliente')
        resultado = InformeFacturacion_ultimaSemana(request, ordenes)
        if resultado is None:
            return redirect('portal:orden-list')
        return resultado
