from io import BytesIO

from django.contrib import messages
from django.http import FileResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View

from accounts.mixins import OperacionRequiredMixin
from core.exceptions import DomainException
from matafuegos.models import Matafuegos
from orden_trabajo.models import Ordenes_de_trabajo
from orden_trabajo.selectors import list_ordenes_recargadas_entre, list_ordenes_ultima_semana
from orden_trabajo.services import (
    cancelar_orden,
    emitir_informe_facturacion,
    emitir_informe_facturacion_ultima_semana,
    emitir_informe_historico_matafuego,
    emitir_informe_orden,
    emitir_informe_recargas,
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


class MatafuegoInformeHistoricoView(OperacionRequiredMixin, View):
    """Historial de tareas realizadas sobre un matafuego a lo largo de todas
    sus ordenes de trabajo cerradas (ver emitir_informe_historico_matafuego)."""

    def get(self, request, matafuego_id):
        matafuego = get_object_or_404(Matafuegos, pk=matafuego_id, company=request.user.company)
        try:
            pdf_bytes = emitir_informe_historico_matafuego(matafuego)
        except DomainException as exc:
            messages.error(request, str(exc))
            return redirect('matafuegos:list')
        messages.success(request, 'Informe emitido')
        return FileResponse(BytesIO(pdf_bytes), as_attachment=True, filename=f'informe_historico_matafuego_{matafuego.numero}.pdf')


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


class OrdenInformeRecargasView(OperacionRequiredMixin, View):
    """Listado de matafuegos recargados (oblea DPS emitida) entre dos fechas
    de cierre de orden, elegidas por el usuario."""

    def get(self, request):
        return render(request, 'orden_trabajo/orden_informe_recargas.html')

    def post(self, request):
        desde = request.POST.get('desde')
        hasta = request.POST.get('hasta')
        if not desde or not hasta:
            messages.error(request, 'Especificar fecha desde y hasta.')
            return redirect('orden_trabajo:orden-informe-recargas')
        qs = list_ordenes_recargadas_entre(request.user.company, desde, hasta)
        try:
            pdf_bytes = emitir_informe_recargas(qs, desde, hasta)
        except DomainException as exc:
            messages.error(request, str(exc))
            return redirect('orden_trabajo:orden-informe-recargas')
        messages.success(request, 'Informe emitido')
        return FileResponse(BytesIO(pdf_bytes), as_attachment=True, filename='informe_recargas.pdf')
