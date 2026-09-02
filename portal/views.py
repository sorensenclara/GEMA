from datetime import date, timedelta

from django.contrib import messages
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.views import LoginView as DjangoLoginView, LogoutView as DjangoLogoutView
from django.contrib.auth.tokens import default_token_generator
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils.crypto import get_random_string
from django.views import View
from django.views.generic import ListView, CreateView, UpdateView, TemplateView, DetailView, FormView

from accounts.auth_forms import StyledAdminPasswordChangeForm, StyledAuthenticationForm
from accounts.forms import UserInviteForm, UserRoleUpdateForm
from accounts.mixins import CompanyAdminRequiredMixin, RoleRequiredMixin
from accounts.models import Role, User
from cliente.models import Cliente
from empresas.forms import CompanyProfileForm
from matafuegos.models import Matafuegos
from orden_trabajo.models import Ordenes_de_trabajo


class LoginView(DjangoLoginView):
    template_name = 'portal/login.html'
    form_class = StyledAuthenticationForm


class LogoutView(DjangoLogoutView):
    next_page = 'portal:login'


class DashboardView(RoleRequiredMixin, TemplateView):
    active_section = 'dashboard'
    template_name = 'portal/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        if user.is_company_admin or user.is_operador:
            company = user.company
            today = date.today()
            horizon = today + timedelta(days=30)
            context['kpi_clientes_activos'] = Cliente.objects.filter(company=company, estado='a').count()
            context['kpi_matafuegos_totales'] = Matafuegos.objects.filter(company=company).count()
            context['kpi_ordenes_pendientes'] = Ordenes_de_trabajo.objects.filter(company=company, estado='p').count()
            context['kpi_vencimientos_30d'] = Matafuegos.objects.filter(company=company).filter(
                Q(fecha_proxima_carga__range=(today, horizon)) | Q(fecha_proxima_ph__range=(today, horizon))
            ).distinct().count()

            estado_labels = dict(Ordenes_de_trabajo._meta.get_field('estado').choices)
            estado_counts = (
                Ordenes_de_trabajo.objects.filter(company=company)
                .values('estado').annotate(total=Count('id')).order_by('estado')
            )
            context['ordenes_por_estado_labels'] = [estado_labels[row['estado']] for row in estado_counts]
            context['ordenes_por_estado_values'] = [row['total'] for row in estado_counts]
            context['mostrar_grafico_ordenes'] = bool(context['ordenes_por_estado_values'])
        return context


class UserListView(CompanyAdminRequiredMixin, ListView):
    active_section = 'usuarios'
    template_name = 'portal/user_list.html'
    context_object_name = 'usuarios'

    def get_queryset(self):
        return User.objects.filter(company=self.request.user.company).order_by('username')


class UserCreateView(CompanyAdminRequiredMixin, CreateView):
    active_section = 'usuarios'
    form_class = UserInviteForm
    template_name = 'portal/user_form.html'
    success_url = reverse_lazy('portal:user-list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['company'] = self.request.user.company
        return kwargs

    def form_valid(self, form):
        user = form.save(commit=False)
        user.company = self.request.user.company
        user.set_password(get_random_string(32))
        user.save()
        self._enviar_invitacion(user)
        messages.success(
            self.request,
            f'Usuario "{user.username}" creado. '
            + ('Se le envió un email para que defina su contraseña.' if user.email else
               'No tiene email cargado: no se pudo enviar la invitación.'),
        )
        return redirect(self.success_url)

    def _enviar_invitacion(self, user):
        if not user.email:
            return
        form = PasswordResetForm({'email': user.email})
        if form.is_valid():
            form.save(
                request=self.request,
                use_https=self.request.is_secure(),
                email_template_name='registration/invite_email.txt',
                subject_template_name='registration/invite_subject.txt',
                token_generator=default_token_generator,
            )


class UserUpdateView(CompanyAdminRequiredMixin, UpdateView):
    active_section = 'usuarios'
    form_class = UserRoleUpdateForm
    template_name = 'portal/user_form.html'
    success_url = reverse_lazy('portal:user-list')

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
    template_name = 'portal/user_password_form.html'

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
        return redirect('portal:user-list')


class UserToggleActiveView(CompanyAdminRequiredMixin, View):
    def post(self, request, pk):
        user = get_object_or_404(User, pk=pk, company=request.user.company)
        if user.pk == request.user.pk:
            messages.error(request, 'No podés desactivar tu propio usuario.')
        else:
            user.is_active = not user.is_active
            user.save(update_fields=['is_active'])
            messages.success(request, f'Usuario "{user.username}" {"activado" if user.is_active else "desactivado"}.')
        return redirect('portal:user-list')


class CompanyProfileUpdateView(CompanyAdminRequiredMixin, UpdateView):
    active_section = 'empresa'
    form_class = CompanyProfileForm
    template_name = 'portal/company_profile.html'
    success_url = reverse_lazy('portal:company-profile')

    def get_object(self, queryset=None):
        return self.request.user.company

    def form_valid(self, form):
        messages.success(self.request, 'Perfil de la compañía actualizado.')
        return super().form_valid(form)


class MisMatafuegosListView(RoleRequiredMixin, ListView):
    active_section = 'mis-matafuegos'
    allowed_roles = [Role.CLIENTE_FINAL]
    template_name = 'portal/mis_matafuegos.html'
    context_object_name = 'matafuegos'

    def get_queryset(self):
        if not self.request.user.cliente_id:
            return Matafuegos.objects.none()
        return Matafuegos.objects.filter(cliente=self.request.user.cliente).order_by('numero')


class MisMatafuegosDetailView(RoleRequiredMixin, DetailView):
    active_section = 'mis-matafuegos'
    allowed_roles = [Role.CLIENTE_FINAL]
    template_name = 'portal/mis_matafuegos_detalle.html'
    context_object_name = 'matafuego'

    def get_queryset(self):
        if not self.request.user.cliente_id:
            return Matafuegos.objects.none()
        return Matafuegos.objects.filter(cliente=self.request.user.cliente)
