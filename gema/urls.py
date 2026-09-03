"""gema URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.shortcuts import redirect
from django.urls import include, path, reverse_lazy

from accounts.forms import (
    StyledAuthenticationForm,
    StyledPasswordResetForm,
    StyledSetPasswordForm,
)
from cliente.views import ClienteAutoComplete
from core.views import DashboardView
from matafuegos.views import MatafuegosAutoComplete


@login_required
def raiz(request):
    if request.user.is_superuser:
        return redirect('empresas:company-list')
    return redirect('dashboard')


urlpatterns = [
    path('', raiz, name='raiz'),
    path('core/', include('core.urls')),
    path('', include('empresas.urls')),
    path('', include('accounts.urls')),
    path('clientes/', include('cliente.urls')),
    path('', include('matafuegos.urls')),
    path('', include('orden_trabajo.urls')),
    path('inicio/', DashboardView.as_view(), name='dashboard'),
    path('cliente/clientes', ClienteAutoComplete.as_view() , name="clientes-autocomplete"),
    path('matafuegos/matafuegos', MatafuegosAutoComplete.as_view() ,name="matafuegos-autocomplete"),
    path('admin/', admin.site.urls),

    path('login/', auth_views.LoginView.as_view(
        template_name='accounts/login.html',
        form_class=StyledAuthenticationForm,
    ), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('password_reset/', auth_views.PasswordResetView.as_view(
        template_name='accounts/password_reset_form.html',
        email_template_name='registration/invite_email.txt',
        subject_template_name='registration/invite_subject.txt',
        form_class=StyledPasswordResetForm,
        success_url=reverse_lazy('password_reset_done'),
    ), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='accounts/password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='accounts/password_reset_confirm.html',
        form_class=StyledSetPasswordForm,
        success_url=reverse_lazy('password_reset_complete')), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(
        template_name='accounts/password_reset_complete.html'), name='password_reset_complete'),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT)
    # Sirve los static/ de cada app (ej. core/static/lexa/...) sin depender
    # de collectstatic ni de que el runner sea justo `manage.py runserver`.
    urlpatterns += staticfiles_urlpatterns()
