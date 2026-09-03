from django.core.exceptions import ValidationError
from django.test import TestCase

from orden_trabajo.models import TareaOrden
from orden_trabajo.tests.factories import OrdenesDeTrabajoFactory, TareaFactory, TareaOrdenFactory


class TareaOrdenFieldsTests(TestCase):
    def test_field_labels(self):
        tarea_orden = TareaOrdenFactory()
        self.assertEqual(tarea_orden._meta.get_field('tarea').verbose_name, 'Tarea')
        self.assertEqual(tarea_orden._meta.get_field('orden').verbose_name, 'Orden')
        self.assertEqual(tarea_orden._meta.get_field('precioAj').verbose_name, 'Precio ajustable')
        self.assertEqual(tarea_orden._meta.get_field('cant_cargada').verbose_name, 'Cantidad cargada')


class TareaOrdenValidationTests(TestCase):
    def test_precio_aj_must_be_non_negative(self):
        tarea_orden = TareaOrden(tarea=TareaFactory(), orden=OrdenesDeTrabajoFactory(), precioAj=-2)
        with self.assertRaises(ValidationError) as ctx:
            tarea_orden.clean()
        self.assertEqual("['El precio debe ser mayor o igual a 0']", str(ctx.exception))

    def test_cant_cargada_must_be_non_negative(self):
        tarea_orden = TareaOrden(tarea=TareaFactory(), orden=OrdenesDeTrabajoFactory(), cant_cargada=-2)
        with self.assertRaises(ValidationError) as ctx:
            tarea_orden.clean()
        self.assertEqual("['La cantidad debe ser mayor o igual a 0']", str(ctx.exception))
