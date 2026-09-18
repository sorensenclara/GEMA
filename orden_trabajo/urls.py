from django.urls import path

from . import views

app_name = 'orden_trabajo'

urlpatterns = [
    path('tareas/', views.TareaListView.as_view(), name='tarea-list'),
    path('tareas/nueva/', views.TareaCreateView.as_view(), name='tarea-create'),
    path('tareas/<int:pk>/editar/', views.TareaUpdateView.as_view(), name='tarea-update'),

    path('ordenes/', views.OrdenListView.as_view(), name='orden-list'),
    path('ordenes/nueva/', views.OrdenCreateView.as_view(), name='orden-create'),
    path('ordenes/<int:pk>/editar/', views.OrdenUpdateView.as_view(), name='orden-update'),
    path('ordenes/<int:pk>/informe/', views.OrdenInformeView.as_view(), name='orden-informe'),
    path('ordenes/<int:pk>/estado/<str:accion>/', views.OrdenCambiarEstadoView.as_view(), name='orden-cambiar-estado'),
    path('ordenes/accion-masiva/', views.OrdenAccionMasivaView.as_view(), name='orden-accion-masiva'),
    path('ordenes/informe-facturacion-ultima-semana/', views.OrdenInformeFacturacionUltimaSemanaView.as_view(), name='orden-informe-facturacion-ultima-semana'),
    path('ordenes/informe-recargas/', views.OrdenInformeRecargasView.as_view(), name='orden-informe-recargas'),
    path('ordenes/matafuego/<int:matafuego_id>/informe-historico/', views.MatafuegoInformeHistoricoView.as_view(), name='matafuego-informe-historico'),
]
