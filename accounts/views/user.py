from django.contrib import messages
from django.contrib.sites.shortcuts import get_current_site
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils.crypto import get_random_string
from django.views import View
from django.views.generic import CreateView, FormView, ListView, UpdateView

from accounts.forms import StyledAdminPasswordChangeForm, UserInviteForm, UserRoleUpdateForm
from accounts.mixins import CompanyAdminRequiredMixin
from accounts.models import User
from accounts.selectors import list_usuarios
from accounts.services import activar_usuario, desactivar_usuario, invitar_usuario
from core.exceptions import DomainException


class UserListView(CompanyAdminRequiredMixin, ListView):
    active_section = 'usuarios'
    template_name = 'accounts/user_list.html'
    context_object_name = 'usuarios'

    def get_queryset(self):
        return list_usuarios(self.request.user.company)


class UserCreateView(CompanyAdminRequiredMixin, CreateView):
    active_section = 'usuarios'
    form_class = UserInviteForm
    template_name = 'accounts/user_form.html'
    success_url = reverse_lazy('accounts:user-list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['company'] = self.request.user.company
        return kwargs

    def form_valid(self, form):
        user = form.save(commit=False)
        user.company = self.request.user.company
        user.set_password(get_random_string(32))
        user.save()
        site = get_current_site(self.request)
        enviada = invitar_usuario(user, domain=site.domain, use_https=self.request.is_secure())
        messages.success(
            self.request,
            f'Usuario "{user.username}" creado. '
            + ('Se le envió un email para que defina su contraseña.' if enviada else
               'No tiene email cargado: no se pudo enviar la invitación.'),
        )
        return redirect(self.success_url)


class UserUpdateView(CompanyAdminRequiredMixin, UpdateView):
    active_section = 'usuarios'
    form_class = UserRoleUpdateForm
    template_name = 'accounts/user_form.html'
    success_url = reverse_lazy('accounts:user-list')

    def get_queryset(self):
        return User.objects.filter(company=self.request.user.company)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['company'] = self.request.user.company
        return kwargs

    def form_valid(self, form):
        messages.success(self.request, f'Usuario "{form.instance.username}" actualizado.')
        return super().form_valid(form)


class UserPasswordChangeView(CompanyAdminRequiredMixin, FormView):
    active_section = 'usuarios'
    form_class = StyledAdminPasswordChangeForm
    template_name = 'accounts/user_password_form.html'

    @property
    def target_user(self):
        if not hasattr(self, '_target_user'):
            self._target_user = get_object_or_404(User, pk=self.kwargs['pk'], company=self.request.user.company)
        return self._target_user

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.target_user
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['target_user'] = self.target_user
        return context

    def form_valid(self, form):
        form.save()
        messages.success(self.request, f'Contraseña de "{self.target_user.username}" actualizada.')
        return redirect('accounts:user-list')


class UserToggleActiveView(CompanyAdminRequiredMixin, View):
    def post(self, request, pk):
        user = get_object_or_404(User, pk=pk, company=request.user.company)
        try:
            if user.is_active:
                desactivar_usuario(user, request.user)
            else:
                activar_usuario(user)
        except DomainException as exc:
            messages.error(request, str(exc))
        else:
            messages.success(request, f'Usuario "{user.username}" {"activado" if user.is_active else "desactivado"}.')
        return redirect('accounts:user-list')
