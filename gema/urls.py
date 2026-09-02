"""gema URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth.decorators import login_required
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.shortcuts import redirect
from django.urls import include, path

from orden_trabajo.views import ClienteAutoComplete, MatafuegosAutoComplete


@login_required
def raiz(request):
    if request.user.is_superuser:
        return redirect('panel:company-list')
    return redirect('portal:dashboard')


urlpatterns = [
    path('', raiz, name='raiz'),
    path('portal/', include('portal.urls')),
    path('panel/', include('panel.urls')),
    path('cliente/clientes', ClienteAutoComplete.as_view() , name="clientes-autocomplete"),
    path('matafuegos/matafuegos', MatafuegosAutoComplete.as_view() ,name="matafuegos-autocomplete"),
    path('admin/', admin.site.urls),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT)
    # Sirve los static/ de cada app (ej. portal/static/lexa/...) sin depender
    # de collectstatic ni de que el runner sea justo `manage.py runserver`.
    urlpatterns += staticfiles_urlpatterns()
