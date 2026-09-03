from io import BytesIO

from django.contrib import messages
from django.http import FileResponse
from django.shortcuts import redirect, render
from django.views import View

from accounts.mixins import OperacionRequiredMixin
from core.exceptions import DomainException
from matafuegos.selectors import (
    list_proximos_vencimientos_carga,
    list_proximos_vencimientos_ph,
    list_vencimiento_entre,
)
from matafuegos.services import emitir_alerta_vencimientos, emitir_informe_proximos_vencimientos


class MatafuegosVencimientosView(OperacionRequiredMixin, View):
    """Alerta de vencimientos entre dos fechas elegidas por el usuario."""

    def get(self, request):
        return render(request, 'matafuegos/matafuegos_vencimientos.html')

    def post(self, request):
        inicio = request.POST.get('inicio')
        fin = request.POST.get('fin')
        if not inicio or not fin:
            messages.error(request, 'Especificar fecha de inicio y fin.')
            return redirect('matafuegos:vencimientos')
        qs = list_vencimiento_entre(request.user.company, inicio, fin)
        try:
            pdf_bytes = emitir_alerta_vencimientos(qs, inicio, fin)
        except DomainException as exc:
            messages.error(request, str(exc))
            return redirect('matafuegos:vencimientos')
        messages.success(request, 'Informe emitido')
        return FileResponse(BytesIO(pdf_bytes), as_attachment=True, filename='alerta_vencimientos.pdf')


class MatafuegosProximosVencimientosView(OperacionRequiredMixin, View):
    def get(self, request):
        carga = list_proximos_vencimientos_carga(request.user.company)
        ph = list_proximos_vencimientos_ph(request.user.company)
        try:
            pdf_bytes = emitir_informe_proximos_vencimientos(carga, ph)
        except DomainException as exc:
            messages.error(request, str(exc))
            return redirect('matafuegos:list')
        messages.success(request, 'Informe emitido')
        return FileResponse(BytesIO(pdf_bytes), as_attachment=True, filename='proximos_vencimientos.pdf')
