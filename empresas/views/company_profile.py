from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import UpdateView

from accounts.mixins import CompanyAdminRequiredMixin
from empresas.forms import CompanyProfileForm


class CompanyProfileUpdateView(CompanyAdminRequiredMixin, UpdateView):
    active_section = 'empresa'
    form_class = CompanyProfileForm
    template_name = 'empresas/company_profile.html'
    success_url = reverse_lazy('empresas:company-profile')

    def get_object(self, queryset=None):
        return self.request.user.company

    def form_valid(self, form):
        messages.success(self.request, 'Perfil de la compañía actualizado.')
        return super().form_valid(form)
