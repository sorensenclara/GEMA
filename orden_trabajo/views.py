from django.shortcuts import render
from dal import autocomplete
# Create your views here.
from cliente.models import Cliente
from matafuegos.models import Matafuegos

class ClienteAutoComplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        # Don't forget to filter out results depending on the visitor !
        if not self.request.user.is_authenticated:
            return Cliente.objects.none()

        # TODO: Unificar filtrado de is_active
        if self.request.user.is_superuser:
            qs = Cliente.objects.all()
        else:
            qs = Cliente.objects.filter(company=self.request.user.company)
        if self.q:
            qs = qs.filter(nombre__istartswith=self.q)
        return qs

class MatafuegosAutoComplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        # Don't forget to filter out results depending on the visitor !
        if not self.request.user.is_authenticated:
            return Matafuegos.objects.none()

        cliente = self.forwarded.get('cliente', None)

        if cliente is not None:
            # TODO: Unificar filtrado de is_active
            qs = Matafuegos.objects.filter(cliente=cliente, vencido=False)
            if not self.request.user.is_superuser:
                qs = qs.filter(company=self.request.user.company)
        else:
            qs = Matafuegos.objects.none()
        if self.q:
            qs = qs.filter(numero__istartswith=self.q)

        return qs
