from django.contrib import messages
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.forms import PasswordResetForm
from django.urls import reverse_lazy
from django.utils.crypto import get_random_string
from django.views.generic import ListView, CreateView, UpdateView

from accounts.mixins import SuperuserRequiredMixin
from accounts.models import Role, User
from empresas.forms import CompanyCreateForm, CompanyRangesForm
from empresas.models import Company


class CompanyListView(SuperuserRequiredMixin, ListView):
    model = Company
    template_name = 'panel/company_list.html'
    context_object_name = 'companies'
    queryset = Company.objects.order_by('nombre')


class CompanyCreateView(SuperuserRequiredMixin, CreateView):
    form_class = CompanyCreateForm
    template_name = 'panel/company_form.html'
    success_url = reverse_lazy('panel:company-list')

    def form_valid(self, form):
        company = form.save()
        admin_user = User(
            username=form.cleaned_data['admin_username'],
            email=form.cleaned_data['admin_email'],
            company=company,
            role=Role.ADMIN_EMPRESA,
        )
        admin_user.set_password(get_random_string(32))
        admin_user.save()
        reset_form = PasswordResetForm({'email': admin_user.email})
        if reset_form.is_valid():
            reset_form.save(
                request=self.request,
                use_https=self.request.is_secure(),
                email_template_name='registration/invite_email.txt',
                subject_template_name='registration/invite_subject.txt',
                token_generator=default_token_generator,
            )
        messages.success(
            self.request,
            f'Compañía "{company.nombre}" creada junto con su admin "{admin_user.username}" '
            '(se le envió un email para definir su contraseña).',
        )
        return super().form_valid(form)


class CompanyUpdateView(SuperuserRequiredMixin, UpdateView):
    model = Company
    form_class = CompanyRangesForm
    template_name = 'panel/company_form.html'
    success_url = reverse_lazy('panel:company-list')

    def form_valid(self, form):
        messages.success(self.request, f'Compañía "{form.instance.nombre}" actualizada.')
        return super().form_valid(form)
