from io import BytesIO

from django.contrib import messages
from django.http import FileResponse
from django.shortcuts import get_object_or_404, redirect
from django.views import View

from accounts.mixins import OperacionRequiredMixin
from core.exceptions import DomainException
from orden_trabajo.models import Ordenes_de_trabajo
from orden_trabajo.selectors import list_ordenes_ultima_semana
from orden_trabajo.services import (
    cancelar_orden,
    emitir_informe_facturacion,
    emitir_informe_facturacion_ultima_semana,
    emitir_informe_orden,
    emitir_oblea_domiciliaria,
    emitir_oblea_vehicular,
    facturar_orden,
    finalizar_orden,
    iniciar_orden,
)


class OrdenInformeView(OperacionRequiredMixin, View):
    def get(self, request, pk):
        orden = get_object_or_404(Ordenes_de_trabajo, pk=pk, company=request.user.company)
        pdf_bytes = emitir_informe_orden(orden)
        messages.success(request, 'Informe emitido')
        return FileResponse(BytesIO(pdf_bytes), as_attachment=True, filename='informe de orden.pdf')


class OrdenAccionMasivaView(OperacionRequiredMixin, View):
    """Acciones que aplican sobre varias órdenes seleccionadas por checkbox
    en el listado (oblea DPS vehicular/domiciliaria, informe de facturación)."""

    ACCIONES = {
        'oblea_vehicular': emitir_oblea_vehicular,
        'oblea_domiciliaria': emitir_oblea_domiciliaria,
        'informe_facturacion': emitir_informe_facturacion,
    }
    NOMBRES_ARCHIVO = {
        'oblea_vehicular': 'oblea_DPS_vehicular.pdf',
        'oblea_domiciliaria': 'oblea_DPS_domiciliaria.pdf',
        'informe_facturacion': 'informe_facturacion.pdf',
    }

    def post(self, request):
        accion = request.POST.get('accion')
        func = self.ACCIONES.get(accion)
        if func is None:
            messages.error(request, 'Acción inválida.')
            return redirect('orden_trabajo:orden-list')
        ids = request.POST.getlist('seleccionadas')
        if not ids:
            messages.error(request, 'Seleccioná al menos una orden.')
            return redirect('orden_trabajo:orden-list')
        qs = Ordenes_de_trabajo.objects.filter(pk__in=ids, company=request.user.company)
        try:
            pdf_bytes = func(qs)
        except DomainException as exc:
            messages.error(request, str(exc))
            return redirect('orden_trabajo:orden-list')
        messages.success(request, 'Informe emitido')
        return FileResponse(BytesIO(pdf_bytes), as_attachment=True, filename=self.NOMBRES_ARCHIVO[accion])


class OrdenCambiarEstadoView(OperacionRequiredMixin, View):
    """Botones de acción rápida del listado: avanzan una orden al siguiente
    estado de su flujo (iniciar/finalizar/cancelar/facturar). La transición
    a "Impresa" no está acá -- es un side-effect de emitir la oblea DPS
    (ver OrdenAccionMasivaView), no una acción de un solo click."""

    ACCIONES = {
        'iniciar': iniciar_orden,
        'finalizar': finalizar_orden,
        'cancelar': cancelar_orden,
        'facturar': facturar_orden,
    }

    def post(self, request, pk, accion):
        orden = get_object_or_404(Ordenes_de_trabajo, pk=pk, company=request.user.company)
        func = self.ACCIONES.get(accion)
        if func is None:
            messages.error(request, 'Acción inválida.')
            return redirect('orden_trabajo:orden-list')
        try:
            func(orden)
        except DomainException as exc:
            messages.error(request, str(exc))
        else:
            messages.success(request, f'Orden N° {orden.id} actualizada.')
        return redirect('orden_trabajo:orden-list')


class OrdenInformeFacturacionUltimaSemanaView(OperacionRequiredMixin, View):
    def get(self, request):
        ordenes = list_ordenes_ultima_semana(request.user.company)
        try:
            pdf_bytes = emitir_informe_facturacion_ultima_semana(ordenes)
        except DomainException as exc:
            messages.error(request, str(exc))
            return redirect('orden_trabajo:orden-list')
        messages.success(request, 'Informe emitido')
        return FileResponse(BytesIO(pdf_bytes), as_attachment=True, filename='informe_facturacion.pdf')
