from django.http import JsonResponse
from django.views import View

from accounts.mixins import OperacionRequiredMixin
from core.services import GeocodingError, buscar_ubicaciones


class ClienteUbicacionBuscarView(OperacionRequiredMixin, View):
    """Proxy server-side hacia el buscador de ubicaciones (ver
    core/services/geocoding.py) para el campo Ubicación/Dirección de
    Nuevo/Editar Cliente. Se llama únicamente cuando el usuario dispara una
    búsqueda explícita (botón Buscar o Enter) -- nunca por cada tecla."""

    def get(self, request):
        texto = request.GET.get('q', '')
        try:
            resultados = buscar_ubicaciones(texto)
        except GeocodingError:
            # Si el proveedor de geocodificación falla, se lo trata igual
            # que "sin resultados": la carga del cliente nunca debe quedar
            # bloqueada por esto, queda disponible la opción manual.
            resultados = []
        return JsonResponse({'resultados': resultados})
