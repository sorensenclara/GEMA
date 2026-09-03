import factory

from cliente.models import Cliente
from empresas.tests.factories import CompanyFactory


class ClienteFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Cliente

    company = factory.SubFactory(CompanyFactory)
    codigo = factory.Sequence(lambda n: str(n + 1))
    nombre = factory.Sequence(lambda n: f'Cliente de prueba {n}')
    cuit_cuil = None
    tipo = 'p'
    estado = 'a'
