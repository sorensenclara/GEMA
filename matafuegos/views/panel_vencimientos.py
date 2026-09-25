from django.core.paginator import Paginator
from django.http import HttpResponse
from django.shortcuts import render
from django.views import View

from accounts.mixins import OperacionRequiredMixin
from cliente.models import Cliente
from core.exceptions import DomainException
from matafuegos.exceptions import ClienteSinWhatsAppException
from matafuegos.models import ESTADOS, TipoMatafuegos
from matafuegos.selectors import (
    aplicar_filtro_vencimientos,
    contar_vencimientos_por_filtro,
    list_panel_vencimientos,
)
from matafuegos.services import exportar_panel_vencimientos_csv, preparar_notificacion

FILTROS_VALIDOS = {'todos', 'proximos', 'vencidos', 'sin_notificar', 'notificados'}
FILAS_POR_PAGINA = 10


class MatafuegosPanelVencimientosView(OperacionRequiredMixin, View):
    """Vista interactiva de Vencimientos: el lugar principal para trabajar
    las notificaciones del día a día, sin tener que entrar a la ficha de
    cada matafuego. La ficha (matafuegos_form.html) mantiene la misma
    acción para cuando se está mirando un matafuego puntual.

    Filtros combinables: la pestaña (Todos/Próximos/Vencidos/Sin notificar/
    Notificados), la búsqueda libre `q` (cliente, código de cliente,
    número de matafuego o tipo) y los desplegables Tipo/Estado/Cliente --
    todos se aplican sobre la misma consulta base, y los 5 contadores de
    las pestañas se calculan siempre sobre esa base (sin recortar por la
    pestaña activa), para que no cambien al cambiar de pestaña.

    `estado` por defecto es 'a' (Activo) -- no tiene mucho sentido
    notificar de entrada un matafuego dado de baja; el desplegable deja
    elegir "Todos los estados" (envía estado='') o "Inactivos" también."""

    active_section = 'matafuegos'
    template_name = 'matafuegos/matafuegos_vencimientos_panel.html'

    def _filtros_get(self, request):
        return {
            'q': request.GET.get('q') or None,
            'tipo': request.GET.get('tipo') or None,
            'estado': request.GET.get('estado', 'a'),
            'cliente': request.GET.get('cliente') or None,
        }

    def get(self, request):
        filtro = request.GET.get('filtro', 'todos')
        if filtro not in FILTROS_VALIDOS:
            filtro = 'todos'
        filtros = self._filtros_get(request)

        todas = list_panel_vencimientos(request.user.company, **filtros)
        counts = contar_vencimientos_por_filtro(todas)
        filas_filtradas = aplicar_filtro_vencimientos(todas, filtro)

        if request.GET.get('exportar') == 'csv':
            csv_bytes = exportar_panel_vencimientos_csv(filas_filtradas)
            response = HttpResponse(csv_bytes, content_type='text/csv; charset=utf-8')
            response['Content-Disposition'] = 'attachment; filename="vencimientos.csv"'
            return response

        # Querystring para los links de las pestañas (conserva q/tipo/estado/
        # cliente pero nunca filtro/page -- cada pestaña pisa su propio
        # filtro y siempre vuelve a la página 1) y para los de paginación
        # (conserva todo menos page).
        qs_sin_filtro = request.GET.copy()
        qs_sin_filtro.pop('filtro', None)
        qs_sin_filtro.pop('page', None)
        qs_sin_pagina = request.GET.copy()
        qs_sin_pagina.pop('page', None)

        paginator = Paginator(filas_filtradas, FILAS_POR_PAGINA)
        pagina = paginator.get_page(request.GET.get('page'))

        for fila in pagina:
            try:
                fila['preview'] = preparar_notificacion(fila['matafuego'])
                fila['error'] = None
                fila['error_tipo'] = None
            except DomainException as exc:
                fila['preview'] = None
                fila['error'] = str(exc)
                # Distingue el caso más común (cliente sin WhatsApp válido,
                # que el template muestra compacto con un link a editar
                # cliente) de cualquier otro DomainException imprevisto, sin
                # tener que adivinar por el texto del mensaje.
                fila['error_tipo'] = 'sin_whatsapp' if isinstance(exc, ClienteSinWhatsAppException) else 'otro'

        context = {
            'filas': pagina,
            'pagina': pagina,
            'filtro_actual': filtro,
            'counts': counts,
            'q': filtros['q'] or '',
            'tipo_actual': filtros['tipo'] or '',
            'estado_actual': filtros['estado'],
            'cliente_actual': filtros['cliente'] or '',
            'tipos': TipoMatafuegos.objects.order_by('tipo'),
            'estados': ESTADOS,
            'clientes': Cliente.objects.filter(company=request.user.company).order_by('nombre'),
            'qs_sin_filtro': qs_sin_filtro.urlencode(),
            'qs_sin_pagina': qs_sin_pagina.urlencode(),
            # Mismo flag de una sola lectura que usa la ficha del matafuego
            # (ver MatafuegosUpdateView): lo dejó MatafuegosNotificarView en
            # la sesión para abrir WhatsApp al volver de notificar desde acá.
            'abrir_whatsapp': request.session.pop('abrir_whatsapp', None),
        }
        return render(request, self.template_name, context)
