from django.test import SimpleTestCase

from core.utils import (
    TelefonoInvalidoException,
    es_telefono_normalizado,
    normalizar_telefono_ar,
    whatsapp_url,
)


class NormalizarTelefonoArTests(SimpleTestCase):
    def test_none_and_blank_devuelven_none(self):
        self.assertIsNone(normalizar_telefono_ar(None))
        self.assertIsNone(normalizar_telefono_ar(''))
        self.assertIsNone(normalizar_telefono_ar('   '))

    def test_diez_digitos_sin_formato_es_el_nsn(self):
        # Caso de la fixture de tests de integracion de cliente.
        self.assertEqual(normalizar_telefono_ar('2233445566'), '5492233445566')

    def test_caba_con_guiones_sin_15(self):
        self.assertEqual(normalizar_telefono_ar('011-4500-1000'), '5491145001000')

    def test_celular_caba_con_15_y_0_inicial(self):
        self.assertEqual(normalizar_telefono_ar('011 15 4500-1000'), '5491145001000')

    def test_celular_mar_del_plata_codigo_de_area_3_digitos(self):
        self.assertEqual(normalizar_telefono_ar('0223 15 456-7890'), '5492234567890')

    def test_ya_en_formato_internacional_es_idempotente(self):
        self.assertEqual(normalizar_telefono_ar('5491145001000'), '5491145001000')

    def test_formato_internacional_con_mas_signo_y_espacios(self):
        self.assertEqual(normalizar_telefono_ar('+54 9 11 4500-1000'), '5491145001000')

    def test_codigo_de_pais_sin_marca_de_celular_igual_se_normaliza(self):
        # Numero fijo cargado ya con 54 pero sin el "9" -- no hay forma de
        # distinguirlo de un celular solo con los digitos, así que se le
        # agrega el "9" igual (documentado como limitacion conocida).
        self.assertEqual(normalizar_telefono_ar('541143210000'), '5491143210000')

    def test_sin_digitos_levanta_excepcion(self):
        with self.assertRaises(TelefonoInvalidoException):
            normalizar_telefono_ar('sin telefono')

    def test_muy_corto_levanta_excepcion(self):
        with self.assertRaises(TelefonoInvalidoException):
            normalizar_telefono_ar('12345')

    def test_doce_digitos_sin_15_ubicable_levanta_excepcion(self):
        with self.assertRaises(TelefonoInvalidoException):
            normalizar_telefono_ar('0' + '2' * 12)


class EsTelefonoNormalizadoTests(SimpleTestCase):
    def test_formato_correcto(self):
        self.assertTrue(es_telefono_normalizado('5491145001000'))

    def test_formatos_incorrectos(self):
        self.assertFalse(es_telefono_normalizado(None))
        self.assertFalse(es_telefono_normalizado(''))
        self.assertFalse(es_telefono_normalizado('011-4500-1000'))
        self.assertFalse(es_telefono_normalizado('54114500100'))


class WhatsappUrlTests(SimpleTestCase):
    def test_devuelve_link_para_numero_normalizado(self):
        self.assertEqual(whatsapp_url('5491145001000'), 'https://wa.me/5491145001000')

    def test_devuelve_none_para_numero_no_normalizado(self):
        self.assertIsNone(whatsapp_url('011-4500-1000'))
        self.assertIsNone(whatsapp_url(None))
