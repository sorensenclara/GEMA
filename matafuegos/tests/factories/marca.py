import factory

from matafuegos.models import MarcaMatafuegos


class MarcaMatafuegosFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = MarcaMatafuegos

    nombre = factory.Sequence(lambda n: f'marca{n}')
