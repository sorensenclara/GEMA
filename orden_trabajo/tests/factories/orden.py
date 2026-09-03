from datetime import date

import factory

from matafuegos.tests.factories import MatafuegosFactory
from orden_trabajo.models import Ordenes_de_trabajo


class OrdenesDeTrabajoFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Ordenes_de_trabajo

    matafuegos = factory.SubFactory(MatafuegosFactory)
    cliente = factory.SelfAttribute('matafuegos.cliente')
    company = factory.SelfAttribute('matafuegos.company')
    fecha_creacion = date(2022, 4, 26)
    fecha_entrega = date(2022, 4, 28)
    fecha_cierre = date(2022, 4, 28)
    estado = 'p'
