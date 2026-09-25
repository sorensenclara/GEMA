from django.urls import path

from . import views

app_name = 'cliente'

urlpatterns = [
    path('', views.ClienteListView.as_view(), name='list'),
    path('listado-pdf/', views.ClienteListadoInformeView.as_view(), name='listado-informe'),
    path('nuevo/', views.ClienteCreateView.as_view(), name='create'),
    path('ubicacion-buscar/', views.ClienteUbicacionBuscarView.as_view(), name='ubicacion-buscar'),
    path('<int:pk>/editar/', views.ClienteUpdateView.as_view(), name='update'),
    path('<int:pk>/activar-desactivar/', views.ClienteToggleActiveView.as_view(), name='toggle-active'),
    path('<int:pk>/informe/', views.ClienteInformeView.as_view(), name='informe'),
    path('<int:pk>/enviar-informe/', views.ClienteEnviarInformeView.as_view(), name='enviar-informe'),
]
