from io import BytesIO

from django.http import FileResponse
from django.views import View
from django.views.generic import ListView

from accounts.mixins import OperacionRequiredMixin
from cliente.selectors import list_clientes
from cliente.services import generar_listado_clientes


class ClienteListView(OperacionRequiredMixin, ListView):
    active_section = 'clientes'
    template_name = 'cliente/cliente_list.html'
    context_object_name = 'clientes'

    def get_queryset(self):
        return list_clientes(self.request.user.company, q=self.request.GET.get('q'))


class ClienteListadoInformeView(OperacionRequiredMixin, View):
    def get(self, request):
        qs = list_clientes(request.user.company, q=request.GET.get('q'))
        pdf_bytes = generar_listado_clientes(qs)
        return FileResponse(BytesIO(pdf_bytes), as_attachment=True, filename='listado_clientes.pdf')
