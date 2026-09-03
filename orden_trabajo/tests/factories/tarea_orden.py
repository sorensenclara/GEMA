import factory

from orden_trabajo.models import TareaOrden
from orden_trabajo.tests.factories.orden import OrdenesDeTrabajoFactory
from orden_trabajo.tests.factories.tarea import TareaFactory


class TareaOrdenFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = TareaOrden

    tarea = factory.SubFactory(TareaFactory)
    orden = factory.SubFactory(OrdenesDeTrabajoFactory)
    precioAj = 0
    cant_cargada = 0
