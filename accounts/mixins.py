from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied

from .models import Role


class RoleRequiredMixin(LoginRequiredMixin):
    """Exige login, compañía activa y (opcionalmente) un rol específico.

    - `allowed_roles`: lista de roles permitidos (vacía = cualquier rol de
      usuario de compañía, pero nunca superadmin salvo `superuser_bypass`).
    - `superuser_bypass`: si es True, el superadmin también puede entrar
      (usado en el panel de superadmin, no en el portal de compañía).
    """

    allowed_roles = []
    superuser_bypass = False
    active_section = None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_section'] = self.active_section
        return context

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        user = request.user
        if user.is_superuser:
            if self.superuser_bypass:
                return super().dispatch(request, *args, **kwargs)
            raise PermissionDenied
        if not user.company_id or not user.company.is_active:
            raise PermissionDenied
        if self.allowed_roles and user.role not in self.allowed_roles:
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)


class CompanyAdminRequiredMixin(RoleRequiredMixin):
    allowed_roles = [Role.ADMIN_EMPRESA]


class OperacionRequiredMixin(RoleRequiredMixin):
    """Admin de compañía y Operador: carga y consulta de datos operativos
    (clientes, matafuegos, tareas, órdenes de trabajo)."""
    allowed_roles = [Role.ADMIN_EMPRESA, Role.OPERADOR]


class SuperuserRequiredMixin(RoleRequiredMixin):
    superuser_bypass = True

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and not request.user.is_superuser:
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)
