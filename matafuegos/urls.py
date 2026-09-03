from django.urls import path

from . import views

app_name = 'matafuegos'

urlpatterns = [
    path('matafuegos/', views.MatafuegosListView.as_view(), name='list'),
    path('matafuegos/listado-pdf/', views.MatafuegosListadoInformeView.as_view(), name='listado-informe'),
    path('matafuegos/nuevo/', views.MatafuegosCreateView.as_view(), name='create'),
    path('matafuegos/<int:pk>/editar/', views.MatafuegosUpdateView.as_view(), name='update'),
    path('matafuegos/<int:pk>/eliminar/', views.MatafuegosEliminarView.as_view(), name='eliminar'),
    path('matafuegos/<int:pk>/activar/', views.MatafuegosActivarView.as_view(), name='activar'),
    path('matafuegos/vencimientos/', views.MatafuegosVencimientosView.as_view(), name='vencimientos'),
    path('matafuegos/proximos-vencimientos/', views.MatafuegosProximosVencimientosView.as_view(), name='proximos-vencimientos'),

    path('mis-matafuegos/', views.MisMatafuegosListView.as_view(), name='mis-matafuegos'),
    path('mis-matafuegos/<int:pk>/', views.MisMatafuegosDetailView.as_view(), name='mis-matafuegos-detalle'),
]
