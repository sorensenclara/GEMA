import factory

from accounts.models import Role, User
from empresas.tests.factories import CompanyFactory


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Sequence(lambda n: f'usuario{n}')
    email = factory.LazyAttribute(lambda o: f'{o.username}@example.com')
    company = factory.SubFactory(CompanyFactory)
    role = Role.OPERADOR
    is_active = True
    password = factory.PostGenerationMethodCall('set_password', 'testpass123')
