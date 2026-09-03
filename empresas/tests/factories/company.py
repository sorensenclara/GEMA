import factory

from empresas.models import Company


class CompanyFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Company

    nombre = factory.Sequence(lambda n: f'Compañía de prueba {n}')
    is_active = True
    veh_prefijo = 'V'
    veh_inicio = 1
    veh_fin = 999
    veh_actual = 1
    dom_prefijo = 'D'
    dom_inicio = 1
    dom_fin = 999
    dom_actual = 1
