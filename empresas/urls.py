from django.urls import path

from . import views

app_name = 'empresas'

urlpatterns = [
    path('empresas/', views.CompanyListView.as_view(), name='company-list'),
    path('empresas/nueva/', views.CompanyCreateView.as_view(), name='company-create'),
    path('empresas/<int:pk>/', views.CompanyUpdateView.as_view(), name='company-update'),
    path('empresa/', views.CompanyProfileUpdateView.as_view(), name='company-profile'),
]
