from django.views.generic import DetailView, ListView

from accounts.mixins import RoleRequiredMixin
from accounts.models import Role
from matafuegos.models import Matafuegos


class MisMatafuegosListView(RoleRequiredMixin, ListView):
    active_section = 'mis-matafuegos'
    allowed_roles = [Role.CLIENTE_FINAL]
    template_name = 'matafuegos/mis_matafuegos.html'
    context_object_name = 'matafuegos'

    def get_queryset(self):
        if not self.request.user.cliente_id:
            return Matafuegos.objects.none()
        return Matafuegos.objects.filter(cliente=self.request.user.cliente).order_by('numero')


class MisMatafuegosDetailView(RoleRequiredMixin, DetailView):
    active_section = 'mis-matafuegos'
    allowed_roles = [Role.CLIENTE_FINAL]
    template_name = 'matafuegos/mis_matafuegos_detalle.html'
    context_object_name = 'matafuego'

    def get_queryset(self):
        if not self.request.user.cliente_id:
            return Matafuegos.objects.none()
        return Matafuegos.objects.filter(cliente=self.request.user.cliente)
