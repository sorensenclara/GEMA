from io import BytesIO

from django.contrib import messages
from django.core.paginator import Paginator
from django.http import FileResponse, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.http import url_has_allowed_host_and_scheme
from django.views import View

from accounts.mixins import OperacionRequiredMixin
from cliente.models import Cliente
from core.exceptions import DomainException
from matafuegos.exceptions import ClienteSinWhatsAppException
from matafuegos.models import ESTADOS, Matafuegos, TipoMatafuegos
from matafuegos.selectors import (
    aplicar_filtro_vencimientos,
    contar_vencimientos_por_filtro,
    list_matafuegos,
    list_panel_vencimientos,
)
from matafuegos.services import (
    activar_matafuego,
    eliminar_matafuego,
    exportar_panel_vencimientos_csv,
    generar_listado_matafuegos,
    preparar_notificacion,
)

FILTROS_VALIDOS = {'todos', 'proximos', 'vencidos', 'sin_notificar', 'notificados'}
FILAS_POR_PAGINA = 10


def _filtros_get(request):
    return {
        'q': request.GET.get('q'),
        'tipo': request.GET.get('tipo'),
        'estado': request.GET.get('estado'),
        'vencido': request.GET.get('vencido'),
    }


def _redirect_back(request, default='matafuegos:list'):
    """Vuelve a la página desde la que se disparó la acción (grilla de
    Matafuegos o la grilla de Matafuegos de un cliente en cliente_form.html),
    o al listado de matafuegos si no hay un referer propio válido."""
    referer = request.META.get('HTTP_REFERER')
    if referer and url_has_allowed_host_and_scheme(referer, allowed_hosts={request.get_host()}, require_https=request.is_secure()):
        return redirect(referer)
    return redirect(default)


class MatafuegosListView(OperacionRequiredMixin, View):
    """Grilla principal de Matafuegos: además del alta/edición de siempre,
    es también el lugar principal para trabajar las notificaciones de
    vencimiento del día a día (pestañas Todos/Próximos/Vencidos/Sin
    notificar/Notificados, búsqueda y filtros de Tipo/Estado/Cliente,
    exportar). Usa la misma lógica que el panel de Vencimientos
    (matafuegos/views/panel_vencimientos.py) -- ver ese archivo para el
    detalle de cómo se arman los contadores y los filtros combinados. La
    diferencia es solo de columnas: acá se muestran Próx. Carga y Próx. PH
    por separado (como en la grilla clásica) en vez de un único
    "Próximo vencimiento", y las acciones de edición/baja/informe histórico
    de siempre en vez del menú "...".

    Importante: al igual que el panel de Vencimientos, esta grilla solo
    muestra matafuegos que tengan cargada alguna fecha de vencimiento
    (fecha_proxima_carga o fecha_proxima_ph) -- un matafuego cuyo Tipo no
    tenga configurado ningún vencimiento (vencimiento_carga/vencimiento_ph
    en TipoMatafuegos) no va a aparecer acá. Antes de este cambio la
    grilla mostraba todos los matafuegos sin esa condición."""

    active_section = 'matafuegos'
    template_name = 'matafuegos/matafuegos_list.html'

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
            response['Content-Disposition'] = 'attachment; filename="matafuegos.csv"'
            return response

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
            # (ver MatafuegosUpdateView) para abrir WhatsApp al volver de
            # notificar desde acá.
            'abrir_whatsapp': request.session.pop('abrir_whatsapp', None),
        }
        return render(request, self.template_name, context)


class MatafuegosListadoInformeView(OperacionRequiredMixin, View):
    def get(self, request):
        qs = list_matafuegos(request.user.company, **_filtros_get(request))
        pdf_bytes = generar_listado_matafuegos(qs)
        return FileResponse(BytesIO(pdf_bytes), as_attachment=True, filename='listado_matafuegos.pdf')


class MatafuegosEliminarView(OperacionRequiredMixin, View):
    def post(self, request, pk):
        matafuego = get_object_or_404(Matafuegos, pk=pk, company=request.user.company)
        numero = matafuego.numero
        eliminado = eliminar_matafuego(matafuego)
        if eliminado:
            messages.success(request, f'Matafuego N° {numero} eliminado.')
        else:
            messages.success(request, f'Matafuego N° {numero} dado de baja (tiene órdenes de trabajo asociadas).')
        return _redirect_back(request)


class MatafuegosActivarView(OperacionRequiredMixin, View):
    def post(self, request, pk):
        matafuego = get_object_or_404(Matafuegos, pk=pk, company=request.user.company)
        activar_matafuego(matafuego)
        messages.success(request, f'Matafuego N° {matafuego.numero} activado.')
        return _redirect_back(request)
