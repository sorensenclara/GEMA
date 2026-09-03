from django.test import TestCase

from matafuegos.tests.factories import CategoriaMatafuegosFactory


class CategoriaMatafuegosModelTests(TestCase):
    def test_field_label(self):
        categoria = CategoriaMatafuegosFactory()
        self.assertEqual(categoria._meta.get_field('nombre').verbose_name, 'Nombre')

    def test_field_max_length(self):
        categoria = CategoriaMatafuegosFactory()
        self.assertEqual(categoria._meta.get_field('nombre').max_length, 20)

    def test_str_returns_nombre(self):
        categoria = CategoriaMatafuegosFactory(nombre='Vehicular')
        self.assertEqual(str(categoria), 'Vehicular')
