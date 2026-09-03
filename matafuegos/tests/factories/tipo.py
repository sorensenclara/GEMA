import factory

from matafuegos.models import TipoMatafuegos
from matafuegos.tests.factories.categoria import CategoriaMatafuegosFactory


class TipoMatafuegosFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = TipoMatafuegos

    tipo = factory.Sequence(lambda n: f'tipo {n}')
    categoria = factory.SubFactory(CategoriaMatafuegosFactory)
    vencimiento_carga = 10
    vencimiento_ph = 20
    volumen = 5.5
    peso = 10
