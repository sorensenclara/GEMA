from datetime import date

import factory

from cliente.tests.factories import ClienteFactory
from matafuegos.models import Matafuegos
from matafuegos.tests.factories.marca import MarcaMatafuegosFactory
from matafuegos.tests.factories.tipo import TipoMatafuegosFactory


class MatafuegosFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Matafuegos

    cliente = factory.SubFactory(ClienteFactory)
    company = factory.SelfAttribute('cliente.company')
    numero = factory.Sequence(lambda n: n + 1)
    numero_dps = factory.Sequence(lambda n: f'd{n}')
    direccion = 'Chacabuco 1147'
    marca = factory.SubFactory(MarcaMatafuegosFactory)
    tipo = factory.SubFactory(TipoMatafuegosFactory)
    categoria = 'd'
    fecha_fabricacion = date(2022, 4, 28)
    fecha_carga = date(2022, 4, 28)
    fecha_ph = date(2022, 4, 28)
