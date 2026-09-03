from io import BytesIO

from django.contrib import messages
from django.http import FileResponse
from django.shortcuts import get_object_or_404, redirect
from django.views import View

from accounts.mixins import OperacionRequiredMixin
from cliente.models import Cliente
from cliente.services import enviar_informe_por_email, generar_informe_cliente
from core.exceptions import DomainException


class ClienteToggleActiveView(OperacionRequiredMixin, View):
    def post(self, request, pk):
        cliente = get_object_or_404(Cliente, pk=pk, company=request.user.company)
        cliente.estado = 'i' if cliente.estado == 'a' else 'a'
        cliente.save(update_fields=['estado'])
        messages.success(request, f'Cliente "{cliente.nombre}" {"activado" if cliente.estado == "a" else "desactivado"}.')
        return redirect('cliente:list')


class ClienteInformeView(OperacionRequiredMixin, View):
    def get(self, request, pk):
        cliente = get_object_or_404(Cliente, pk=pk, company=request.user.company)
        pdf_bytes = generar_informe_cliente(cliente)
        return FileResponse(BytesIO(pdf_bytes), as_attachment=True, filename=f'informe_{cliente.codigo}.pdf')


class ClienteEnviarInformeView(OperacionRequiredMixin, View):
    def post(self, request, pk):
        cliente = get_object_or_404(Cliente, pk=pk, company=request.user.company)
        try:
            pdf_bytes = enviar_informe_por_email(cliente)
        except DomainException as exc:
            messages.error(request, str(exc))
            return redirect('cliente:list')
        messages.success(request, 'Email enviado correctamente')
        return FileResponse(BytesIO(pdf_bytes), as_attachment=True, filename='Informe cliente.pdf')
