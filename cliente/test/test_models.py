import unittest

from django.core.exceptions import ValidationError
from django.test import TestCase

from cliente.models import Cliente
from empresas.models import Company


class ClienteModelTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        #Set up non-modified objects used by all test methods
        company = Company.objects.create(nombre='Compañía de prueba')
        Cliente.objects.create(company=company, codigo=1, cuit_cuil='20115225691', telefono=2222, nombre='Big', direccion='San Lorenzo 516',tipo="p", estado='i')
    pass

    def test_codigo_label(self):
        cliente = Cliente.objects.get(codigo=1)
        field_label = cliente._meta.get_field('codigo').verbose_name
        self.assertEquals(field_label,'Codigo')

    def test_cuit_cuil_label(self):
        cliente = Cliente.objects.get(codigo=1)
        field_label = cliente._meta.get_field('cuit_cuil').verbose_name
        self.assertEquals(field_label,'CUIT/CUIL')

    def test_cuit_cuil_max_length(self):
        cliente=Cliente.objects.get(codigo=1)
        max_length = cliente._meta.get_field('cuit_cuil').max_length
        self.assertEquals(max_length,11)

    def test_nombre_label(self):
        cliente = Cliente.objects.get(codigo=1)
        field_label = cliente._meta.get_field('nombre').verbose_name
        self.assertEquals(field_label,'Nombre/ Razón Social')

    def test_nombre_max_length(self):
        cliente=Cliente.objects.get(codigo=1)
        max_length = cliente._meta.get_field('nombre').max_length
        self.assertEquals(max_length,80)

    def test_contacto_label(self):
        cliente = Cliente.objects.get(codigo=1)
        field_label = cliente._meta.get_field('contacto').verbose_name
        self.assertEquals(field_label,'Nombre contacto')

    def test_contacto_max_length(self):
        cliente = Cliente.objects.get(codigo=1)
        max_length = cliente._meta.get_field('contacto').max_length
        self.assertEquals(max_length,80)

    def test_direccion_label(self):
        cliente = Cliente.objects.get(codigo=1)
        field_label = cliente._meta.get_field('direccion').verbose_name
        self.assertEquals(field_label,'Dirección')

    def test_direccion_max_length(self):
        cliente = Cliente.objects.get(codigo=1)
        max_length = cliente._meta.get_field('direccion').max_length
        self.assertEquals(max_length,80)

    def test_telefono_label(self):
        cliente = Cliente.objects.get(codigo=1)
        field_label = cliente._meta.get_field('telefono').verbose_name
        self.assertEquals(field_label,'Telefono')

    def test_telefono_max_length(self):
        cliente = Cliente.objects.get(codigo=1)
        max_length = cliente._meta.get_field('telefono').max_length
        self.assertEquals(max_length, 80)

    def test_email_label(self):
        cliente = Cliente.objects.get(codigo=1)
        field_label = cliente._meta.get_field('email').verbose_name
        self.assertEquals(field_label,'Email')

    def test_email_max_length(self):
        cliente=Cliente.objects.get(codigo=1)
        max_length = cliente._meta.get_field('email').max_length
        self.assertEquals(max_length,264)

    def test_web_label(self):
        cliente = Cliente.objects.get(codigo=1)
        field_label = cliente._meta.get_field('web').verbose_name
        self.assertEquals(field_label,'Web')

    def test_web_max_length(self):
        cliente = Cliente.objects.get(codigo=1)
        max_length = cliente._meta.get_field('web').max_length
        self.assertEquals(max_length,200)

    def test_tipo_label(self):
        cliente = Cliente.objects.get(codigo=1)
        field_label = cliente._meta.get_field('tipo').verbose_name
        self.assertEquals(field_label,'Tipo')

    def test_tipo_max_length(self):
        cliente = Cliente.objects.get(codigo=1)
        max_length = cliente._meta.get_field('tipo').max_length
        self.assertEquals(max_length,80)

    def test_estado_label(self):
        cliente = Cliente.objects.get(codigo=1)
        field_label = cliente._meta.get_field('estado').verbose_name
        self.assertEquals(field_label,'Estado')
    def test_estado_max_length(self):
        cliente = Cliente.objects.get(codigo=1)
        max_length = cliente._meta.get_field('estado').max_length
        self.assertEquals(max_length,80)

    def test_get_absolute_url(self):
        cliente=Cliente.objects.get(codigo=1)

    def test_fecha_fabricacion(self):
        c = Cliente(codigo=-1,
                    cuit_cuil='20115225691',
                    telefono=2222,
                    nombre='Big',
                    direccion='San Lorenzo 516',
                    tipo="p",
                    estado='i')
        with self.assertRaises(ValidationError) as e:
            c.clean()
        self.assertEqual("['El codigo del cliente debe ser mayor a 0']",str(e.exception))

    def test_cuit_1(self):
        c = Cliente(codigo=1,
                    cuit_cuil='10101001001',
                    telefono=2222,
                    nombre='Big',
                    direccion='San Lorenzo 516',
                    tipo="p",
                    estado='i')
        with self.assertRaises(ValidationError) as e:
            c.clean()
        self.assertEqual("['El cuit_cuil del cliente es invalido']",str(e.exception))

    def test_cuit_2(self):
        c = Cliente(codigo=1,
                    cuit_cuil='1010100101',
                    telefono=2222,
                    nombre='Big',
                    direccion='San Lorenzo 516',
                    tipo="p",
                    estado='i')
        with self.assertRaises(ValidationError) as e:
            c.clean()
        self.assertEqual("['El cuit_cuil del cliente es invalido']",str(e.exception))
