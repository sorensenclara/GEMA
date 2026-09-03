from django.contrib import messages
from django.contrib.sites.shortcuts import get_current_site
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, UpdateView

from accounts.mixins import SuperuserRequiredMixin
from empresas.forms import CompanyCreateForm, CompanyRangesForm
from empresas.models import Company
from empresas.selectors import list_companies
from empresas.services import crear_company_con_admin


class CompanyListView(SuperuserRequiredMixin, ListView):
    template_name = 'empresas/company_list.html'
    context_object_name = 'companies'

    def get_queryset(self):
        return list_companies()


class CompanyCreateView(SuperuserRequiredMixin, CreateView):
    form_class = CompanyCreateForm
    template_name = 'empresas/company_form.html'
    success_url = reverse_lazy('empresas:company-list')

    def form_valid(self, form):
        company = form.save(commit=False)
        site = get_current_site(self.request)
        company, admin_user = crear_company_con_admin(
            company,
            admin_username=form.cleaned_data['admin_username'],
            admin_email=form.cleaned_data['admin_email'],
            domain=site.domain,
            use_https=self.request.is_secure(),
        )
        self.object = company
        messages.success(
            self.request,
            f'Compañía "{company.nombre}" creada junto con su admin "{admin_user.username}" '
            '(se le envió un email para definir su contraseña).',
        )
        return HttpResponseRedirect(self.get_success_url())


class CompanyUpdateView(SuperuserRequiredMixin, UpdateView):
    model = Company
    form_class = CompanyRangesForm
    template_name = 'empresas/company_form.html'
    success_url = reverse_lazy('empresas:company-list')

    def form_valid(self, form):
        messages.success(self.request, f'Compañía "{form.instance.nombre}" actualizada.')
        return super().form_valid(form)
