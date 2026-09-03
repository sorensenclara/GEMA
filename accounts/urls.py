from django.urls import path

from . import views

app_name = 'accounts'

urlpatterns = [
    path('usuarios/', views.UserListView.as_view(), name='user-list'),
    path('usuarios/nuevo/', views.UserCreateView.as_view(), name='user-create'),
    path('usuarios/<int:pk>/editar/', views.UserUpdateView.as_view(), name='user-update'),
    path('usuarios/<int:pk>/cambiar-password/', views.UserPasswordChangeView.as_view(), name='user-password-change'),
    path('usuarios/<int:pk>/activar-desactivar/', views.UserToggleActiveView.as_view(), name='user-toggle-active'),
]
