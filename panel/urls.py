from django.urls import path

from . import views

app_name = 'panel'

urlpatterns = [
    path('empresas/', views.CompanyListView.as_view(), name='company-list'),
    path('empresas/nueva/', views.CompanyCreateView.as_view(), name='company-create'),
    path('empresas/<int:pk>/', views.CompanyUpdateView.as_view(), name='company-update'),
]
