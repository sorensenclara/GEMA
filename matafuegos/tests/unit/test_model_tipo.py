from django.core.exceptions import ValidationError
from django.test import TestCase

from matafuegos.models import TipoMatafuegos
from matafuegos.tests.factories import TipoMatafuegosFactory


class TipoMatafuegosFieldsTests(TestCase):
    def test_field_labels(self):
        tipo = TipoMatafuegosFactory()
        labels = {
            'tipo': 'Tipo',
            'categoria': 'Categoria',
            'vencimiento_carga': 'Vencimiento de carga',
            'vencimiento_ph': 'Vencimiento de PH',
            'volumen': 'Volumen',
            'peso': 'Peso',
        }
        for field_name, expected in labels.items():
            with self.subTest(field=field_name):
                self.assertEqual(tipo._meta.get_field(field_name).verbose_name, expected)

    def test_tipo_max_length(self):
        tipo = TipoMatafuegosFactory()
        self.assertEqual(tipo._meta.get_field('tipo').max_length, 20)

    def test_str_returns_tipo(self):
        tipo = TipoMatafuegosFactory(tipo='ABC en polvo')
        self.assertEqual(str(tipo), 'ABC en polvo')


class TipoMatafuegosValidationTests(TestCase):
    def test_vencimiento_carga_must_be_positive(self):
        tipo = TipoMatafuegos(tipo='tipo 1', vencimiento_carga=-10, vencimiento_ph=20, volumen=5.5, peso=10)
        with self.assertRaises(ValidationError) as ctx:
            tipo.clean()
        self.assertEqual("['El numero de dias de vencimeinto de carga debe ser mayor a 0']", str(ctx.exception))

    def test_vencimiento_ph_must_be_positive(self):
        tipo = TipoMatafuegos(tipo='tipo 1', vencimiento_carga=10, vencimiento_ph=-20, volumen=5.5, peso=10)
        with self.assertRaises(ValidationError) as ctx:
            tipo.clean()
        self.assertEqual("['El numero de dias de vencimeinto de ph debe ser mayor a 0']", str(ctx.exception))

    def test_volumen_must_be_positive(self):
        tipo = TipoMatafuegos(tipo='tipo 1', vencimiento_carga=10, vencimiento_ph=20, volumen=-5.5, peso=10)
        with self.assertRaises(ValidationError) as ctx:
            tipo.clean()
        self.assertEqual("['El volumen debe ser mayor a 0']", str(ctx.exception))

    def test_peso_must_be_positive(self):
        tipo = TipoMatafuegos(tipo='tipo 1', vencimiento_carga=10, vencimiento_ph=20, volumen=5.5, peso=-10)
        with self.assertRaises(ValidationError) as ctx:
            tipo.clean()
        self.assertEqual("['El peso debe ser mayor a 0']", str(ctx.exception))
