from django.contrib.auth import views as auth_views
from django.urls import path, reverse_lazy

from accounts.auth_forms import StyledPasswordResetForm, StyledSetPasswordForm
from . import views, views_operacion

app_name = 'portal'

urlpatterns = [
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('', views.DashboardView.as_view(), name='dashboard'),

    path('usuarios/', views.UserListView.as_view(), name='user-list'),
    path('usuarios/nuevo/', views.UserCreateView.as_view(), name='user-create'),
    path('usuarios/<int:pk>/editar/', views.UserUpdateView.as_view(), name='user-update'),
    path('usuarios/<int:pk>/cambiar-password/', views.UserPasswordChangeView.as_view(), name='user-password-change'),
    path('usuarios/<int:pk>/activar-desactivar/', views.UserToggleActiveView.as_view(), name='user-toggle-active'),

    path('empresa/', views.CompanyProfileUpdateView.as_view(), name='company-profile'),

    path('mis-matafuegos/', views.MisMatafuegosListView.as_view(), name='mis-matafuegos'),
    path('mis-matafuegos/<int:pk>/', views.MisMatafuegosDetailView.as_view(), name='mis-matafuegos-detalle'),

    path('clientes/', views_operacion.ClienteListView.as_view(), name='cliente-list'),
    path('clientes/listado-pdf/', views_operacion.ClienteListadoInformeView.as_view(), name='cliente-listado-informe'),
    path('clientes/nuevo/', views_operacion.ClienteCreateView.as_view(), name='cliente-create'),
    path('clientes/<int:pk>/editar/', views_operacion.ClienteUpdateView.as_view(), name='cliente-update'),
    path('clientes/<int:pk>/activar-desactivar/', views_operacion.ClienteToggleActiveView.as_view(), name='cliente-toggle-active'),
    path('clientes/<int:pk>/informe/', views_operacion.ClienteInformeView.as_view(), name='cliente-informe'),
    path('clientes/<int:pk>/enviar-informe/', views_operacion.ClienteEnviarInformeView.as_view(), name='cliente-enviar-informe'),

    path('matafuegos/', views_operacion.MatafuegosListView.as_view(), name='matafuegos-list'),
    path('matafuegos/listado-pdf/', views_operacion.MatafuegosListadoInformeView.as_view(), name='matafuegos-listado-informe'),
    path('matafuegos/nuevo/', views_operacion.MatafuegosCreateView.as_view(), name='matafuegos-create'),
    path('matafuegos/<int:pk>/editar/', views_operacion.MatafuegosUpdateView.as_view(), name='matafuegos-update'),
    path('matafuegos/vencimientos/', views_operacion.MatafuegosVencimientosView.as_view(), name='matafuegos-vencimientos'),
    path('matafuegos/proximos-vencimientos/', views_operacion.MatafuegosProximosVencimientosView.as_view(), name='matafuegos-proximos-vencimientos'),

    path('tareas/', views_operacion.TareaListView.as_view(), name='tarea-list'),
    path('tareas/nueva/', views_operacion.TareaCreateView.as_view(), name='tarea-create'),
    path('tareas/<int:pk>/editar/', views_operacion.TareaUpdateView.as_view(), name='tarea-update'),

    path('ordenes/', views_operacion.OrdenListView.as_view(), name='orden-list'),
    path('ordenes/nueva/', views_operacion.OrdenCreateView.as_view(), name='orden-create'),
    path('ordenes/<int:pk>/editar/', views_operacion.OrdenUpdateView.as_view(), name='orden-update'),
    path('ordenes/<int:pk>/informe/', views_operacion.OrdenInformeView.as_view(), name='orden-informe'),
    path('ordenes/accion-masiva/', views_operacion.OrdenAccionMasivaView.as_view(), name='orden-accion-masiva'),
    path('ordenes/informe-facturacion-ultima-semana/', views_operacion.OrdenInformeFacturacionUltimaSemanaView.as_view(), name='orden-informe-facturacion-ultima-semana'),

    path('password_reset/', auth_views.PasswordResetView.as_view(
        template_name='portal/password_reset_form.html',
        email_template_name='registration/invite_email.txt',
        subject_template_name='registration/invite_subject.txt',
        form_class=StyledPasswordResetForm,
        success_url=reverse_lazy('portal:password_reset_done'),
    ), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='portal/password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='portal/password_reset_confirm.html',
        form_class=StyledSetPasswordForm,
        success_url=reverse_lazy('portal:password_reset_complete')), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(
        template_name='portal/password_reset_complete.html'), name='password_reset_complete'),
]
