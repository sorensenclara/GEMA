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
            'localidad': 'Localidad',
            'provincia': 'Provincia',
            'codigo_postal': 'Código postal',
            'pais': 'País',
            'geo_referencia_externa': 'Referencia externa de ubicación',
            'geo_provider': 'Proveedor de geocodificación',
            'geo_status': 'Estado de georreferenciación',
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
            'cuit_cuil': 11, 'nombre': 80, 'contacto': 80, 'direccion': 255,
            'localidad': 120, 'provincia': 120, 'codigo_postal': 20, 'pais': 80,
            'geo_referencia_externa': 50, 'geo_provider': 30, 'geo_status': 25,
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


class ClienteTelefonoNormalizationTests(TestCase):
    """clean() deja el telefono siempre listo para WhatsApp (ver charla con
    Clara, 2026-09-22) -- la normalizacion en si se prueba a fondo en
    core/tests/unit/test_utils_telefono.py, aca solo se prueba que el
    modelo la aplique y falle prolijo cuando no se puede."""

    def test_clean_normaliza_el_telefono(self):
        cliente = Cliente(codigo='1', nombre='Big', tipo='p', estado='i', telefono='011 15 4500-1000')
        cliente.clean()
        self.assertEqual(cliente.telefono, '5491145001000')

    def test_clean_es_idempotente(self):
        cliente = Cliente(codigo='1', nombre='Big', tipo='p', estado='i', telefono='5491145001000')
        cliente.clean()
        self.assertEqual(cliente.telefono, '5491145001000')

    def test_clean_acepta_telefono_vacio(self):
        cliente = Cliente(codigo='1', nombre='Big', tipo='p', estado='i', telefono=None)
        cliente.clean()  # no debe lanzar
        self.assertIsNone(cliente.telefono)

    def test_clean_raises_for_invalid_telefono(self):
        cliente = Cliente(codigo='1', nombre='Big', tipo='p', estado='i', telefono='sin telefono')
        with self.assertRaises(ValidationError) as ctx:
            cliente.clean()
        self.assertIn('telefono', ctx.exception.message_dict)


class ClienteGeoStatusChoicesTests(TestCase):
    """Solo deben existir los 3 estados que se pueden producir en el flujo
    real (ver charla con Clara, 2026-09-23): no agregar 'pendiente' ni
    ningún otro que no salga de una carga real de Cliente."""

    def test_choices_son_exactamente_las_tres_acordadas(self):
        choices = dict(Cliente._meta.get_field('geo_status').choices)
        self.assertEqual(
            choices,
            {
                'georreferenciado': 'Georreferenciado',
                'manual_legado': 'Manual (legado)',
                'manual_no_encontrado': 'Manual (no encontrado)',
            },
        )
