from django.views.generic import TemplateView

from accounts.mixins import RoleRequiredMixin
from cliente.selectors import count_clientes_activos, count_clientes_sin_actividad
from core.selectors import recent_activity
from matafuegos.selectors import count_matafuegos, count_vencimiento_proximo
from orden_trabajo.models import Ordenes_de_trabajo
from orden_trabajo.selectors import count_ordenes_pendientes, ordenes_por_estado


PERIODOS_ORDENES_VALIDOS = {30, 60, 90}


class DashboardView(RoleRequiredMixin, TemplateView):
    active_section = 'dashboard'
    template_name = 'core/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        if user.is_company_admin or user.is_operador:
            company = user.company
            context['kpi_clientes_activos'] = count_clientes_activos(company)
            context['kpi_matafuegos_totales'] = count_matafuegos(company)
            context['kpi_ordenes_pendientes'] = count_ordenes_pendientes(company)
            context['kpi_vencimientos_30d'] = count_vencimiento_proximo(company)
            context['kpi_clientes_sin_actividad'] = count_clientes_sin_actividad(company)
            context['actividad_reciente'] = recent_activity(company, limit=15)

            # Filtro de período del gráfico "Órdenes de trabajo por estado"
            # (select del dashboard, antes deshabilitado) -- 30/60/90 días o
            # sin valor = todo el historial. Cualquier otro valor recibido
            # por GET se ignora en vez de romper la página.
            periodo_ordenes_raw = self.request.GET.get('periodo_ordenes')
            periodo_ordenes = int(periodo_ordenes_raw) if periodo_ordenes_raw and periodo_ordenes_raw.isdigit() else None
            if periodo_ordenes not in PERIODOS_ORDENES_VALIDOS:
                periodo_ordenes = None
            context['periodo_ordenes_actual'] = periodo_ordenes

            estado_labels = dict(Ordenes_de_trabajo._meta.get_field('estado').choices)
            estado_counts = ordenes_por_estado(company, periodo_dias=periodo_ordenes)
            context['ordenes_por_estado_labels'] = [estado_labels[row['estado']] for row in estado_counts]
            context['ordenes_por_estado_values'] = [row['total'] for row in estado_counts]
            context['mostrar_grafico_ordenes'] = bool(context['ordenes_por_estado_values'])

            # Total y filas (label/valor/porcentaje/color) para la leyenda HTML
            # del donut -- el grafico en si lo dibuja Morris.js con estos mismos
            # colores (ver dashboard.html), separado para no acoplar el color
            # al valor de 'estado' (que no viaja mas alla de esta vista).
            total_ordenes = sum(context['ordenes_por_estado_values'])
            context['ordenes_por_estado_total'] = total_ordenes
            paleta_estados = ['#1B4B8D', '#2E6FE0', '#9FC9EA', '#0C3A84', '#EC6C05']
            context['ordenes_por_estado_rows'] = [
                {
                    'label': label,
                    'value': value,
                    'pct': round(value * 100 / total_ordenes) if total_ordenes else 0,
                    'color': paleta_estados[i % len(paleta_estados)],
                }
                for i, (label, value) in enumerate(zip(
                    context['ordenes_por_estado_labels'],
                    context['ordenes_por_estado_values'],
                ))
            ]
        return context
