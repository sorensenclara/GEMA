from dal import autocomplete

from cliente.models import Cliente


class ClienteAutoComplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
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
