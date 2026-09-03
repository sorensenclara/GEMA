from django.core.exceptions import ValidationError
from django.test import TestCase

from cliente.models import Cliente
from cliente.tests.factories import ClienteFactory


class ClienteFieldsTests(TestCase):
    """Coincide con la forma del modelo (verbose_name/max_length) -- si esto
    se rompe, algo cambió el campo sin que fuera intencional."""

    @classmethod
    def setUpTestData(cls):
        cls.cliente = ClienteFactory()

    def test_field_labels(self):
        labels = {
            'codigo': 'Codigo',
            'cuit_cuil': 'CUIT/CUIL',
            'nombre': 'Nombre/ Razón Social',
            'contacto': 'Nombre contacto',
            'direccion': 'Dirección',
            'telefono': 'Telefono',
            'email': 'Email',
            'web': 'Web',
            'tipo': 'Tipo',
            'estado': 'Estado',
        }
        for field_name, expected_label in labels.items():
            with self.subTest(field=field_name):
                self.assertEqual(self.cliente._meta.get_field(field_name).verbose_name, expected_label)

    def test_field_max_lengths(self):
        max_lengths = {
            'cuit_cuil': 11, 'nombre': 80, 'contacto': 80, 'direccion': 80,
            'telefono': 80, 'email': 264, 'web': 200, 'tipo': 80, 'estado': 80,
        }
        for field_name, expected_max_length in max_lengths.items():
            with self.subTest(field=field_name):
                self.assertEqual(self.cliente._meta.get_field(field_name).max_length, expected_max_length)

    def test_str_includes_nombre_and_codigo(self):
        cliente = ClienteFactory(nombre='Big', codigo='1')
        self.assertEqual(str(cliente), 'Big - 1')


class ClienteCuitValidationTests(TestCase):
    def test_clean_raises_for_invalid_cuit(self):
        cliente = Cliente(codigo='1', cuit_cuil='10101001001', nombre='Big', tipo='p', estado='i')
        with self.assertRaises(ValidationError) as ctx:
            cliente.clean()
        self.assertEqual("['El cuit_cuil del cliente es invalido']", str(ctx.exception))

    def test_clean_raises_for_another_invalid_cuit(self):
        cliente = Cliente(codigo='1', cuit_cuil='1010100101', nombre='Big', tipo='p', estado='i')
        with self.assertRaises(ValidationError) as ctx:
            cliente.clean()
        self.assertEqual("['El cuit_cuil del cliente es invalido']", str(ctx.exception))

    def test_clean_accepts_none_cuit(self):
        cliente = Cliente(codigo='1', cuit_cuil=None, nombre='Big', tipo='p', estado='i')
        cliente.clean()  # no debe lanzar

    def test_validar_cuit_with_correct_check_digit(self):
        cliente = Cliente()
        # CUIT construido con el dígito verificador correcto para esta base.
        self.assertTrue(cliente.validar_cuit('20111111112'))
