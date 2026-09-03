import factory

from matafuegos.models import CategoriaMatafuegos


class CategoriaMatafuegosFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = CategoriaMatafuegos

    nombre = factory.Sequence(lambda n: f'categoria {n}')
