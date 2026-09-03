from dal import autocomplete

from matafuegos.models import Matafuegos


class MatafuegosAutoComplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
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
