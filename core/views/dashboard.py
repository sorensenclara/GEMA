from django.views.generic import TemplateView

from accounts.mixins import RoleRequiredMixin
from cliente.selectors import count_clientes_activos
from matafuegos.selectors import count_matafuegos, count_vencimiento_proximo
from orden_trabajo.models import Ordenes_de_trabajo
from orden_trabajo.selectors import count_ordenes_pendientes, ordenes_por_estado


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

            estado_labels = dict(Ordenes_de_trabajo._meta.get_field('estado').choices)
            estado_counts = ordenes_por_estado(company)
            context['ordenes_por_estado_labels'] = [estado_labels[row['estado']] for row in estado_counts]
            context['ordenes_por_estado_values'] = [row['total'] for row in estado_counts]
            context['mostrar_grafico_ordenes'] = bool(context['ordenes_por_estado_values'])
        return context
