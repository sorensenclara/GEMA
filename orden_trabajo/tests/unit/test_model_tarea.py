from django.core.exceptions import ValidationError
from django.test import TestCase

from orden_trabajo.models import Tarea
from orden_trabajo.tests.factories import TareaFactory


class TareaFieldsTests(TestCase):
    def test_nombre_label(self):
        tarea = TareaFactory()
        self.assertEqual(tarea._meta.get_field('nombre').verbose_name, 'Nombre')

    def test_nombre_max_length(self):
        tarea = TareaFactory()
        self.assertEqual(tarea._meta.get_field('nombre').max_length, 120)

    def test_precio_label(self):
        tarea = TareaFactory()
        self.assertEqual(tarea._meta.get_field('precio').verbose_name, 'Precio')

    def test_str_includes_nombre_and_precio(self):
        tarea = TareaFactory(nombre='limpiar', precio=100)
        self.assertEqual(str(tarea), 'limpiar - $100')


class TareaValidationTests(TestCase):
    def test_precio_must_be_positive(self):
        tarea = Tarea(nombre='limpiar', precio=-100)
        with self.assertRaises(ValidationError) as ctx:
            tarea.clean()
        self.assertEqual("['El precio debe ser mayor a 0']", str(ctx.exception))
