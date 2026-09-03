import factory

from empresas.tests.factories import CompanyFactory
from orden_trabajo.models import Tarea


class TareaFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Tarea

    company = factory.SubFactory(CompanyFactory)
    nombre = factory.Sequence(lambda n: f'tarea {n}')
    precio = 100
    es_recarga = False
