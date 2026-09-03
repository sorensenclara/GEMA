from django.test import TestCase

from matafuegos.tests.factories import MarcaMatafuegosFactory


class MarcaMatafuegosModelTests(TestCase):
    def test_field_label(self):
        marca = MarcaMatafuegosFactory()
        self.assertEqual(marca._meta.get_field('nombre').verbose_name, 'Nombre')

    def test_field_max_length(self):
        marca = MarcaMatafuegosFactory()
        self.assertEqual(marca._meta.get_field('nombre').max_length, 15)

    def test_str_returns_nombre(self):
        marca = MarcaMatafuegosFactory(nombre='Ansul')
        self.assertEqual(str(marca), 'Ansul')
