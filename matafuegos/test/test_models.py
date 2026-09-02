from django.test import TestCase
from matafuegos.models import Matafuegos, MarcaMatafuegos, CategoriaMatafuegos, TipoMatafuegos
from cliente.models import Cliente
from empresas.models import Company
from datetime import timedelta, datetime, date

from django.core.exceptions import ValidationError


class YourTestClass(TestCase):

    @classmethod
    def setUpTestData(cls):

        company = Company.objects.create(nombre='Compañía de prueba')

        marca = MarcaMatafuegos.objects.create(nombre = 'abc')

        categoria = CategoriaMatafuegos.objects.create(nombre = 'categoria 1')

        tipo = TipoMatafuegos.objects.create(tipo = 'tipo 1',
                                             categoria = categoria,
                                             vencimiento_carga = 10,
                                             vencimiento_ph = 20,
                                             volumen = 5.5,
                                             peso = 10)

        cliente = Cliente.objects.create(company = company,
                               codigo = 789,
                               cuit_cuil = 987,
                               nombre = 'Victoria Dell Oso',
                               direccion = 'chacabuco 1147',
                               telefono = '2492565089',
                               email = 'maylendelloso@gmail.com',
                               tipo = 'Persona',
                               estado = 'Activo')

        Matafuegos.objects.create(company = company,
                                  numero = 987,
                                  numero_dps = 'd8',
                                  cliente = cliente,
                                  direccion = 'chacabuco 1147',
                                  marca = marca,
                                  tipo = tipo,
                                  categoria = 'd',
                                  fecha_fabricacion = date(2022,4,28),
                                  fecha_carga = date(2022,4,28),
                                  fecha_ph = date(2022,4,28))
        pass

    # MATAFUEGOS

    # ETIQUETAS ------------------------------------------------------------------------------------------------

    def test_numero_label(self):
        matafuegos=Matafuegos.objects.get(id=1)
        field_label = matafuegos._meta.get_field('numero').verbose_name
        self.assertEquals(field_label,'Numero')

    def test_numero_interno_label(self):
        matafuegos=Matafuegos.objects.get(id=1)
        field_label = matafuegos._meta.get_field('numeroInterno').verbose_name
        self.assertEquals(field_label,'Numero interno')

    def test_numero_dps_label(self):
        matafuegos=Matafuegos.objects.get(id=1)
        field_label = matafuegos._meta.get_field('numero_dps').verbose_name
        self.assertEquals(field_label,'Numero de DPS')

    def test_cliente_label(self):
        matafuegos=Matafuegos.objects.get(id=1)
        field_label = matafuegos._meta.get_field('cliente').verbose_name
        self.assertEquals(field_label,'Cliente')

    def test_patente_label(self):
        matafuegos=Matafuegos.objects.get(id=1)
        field_label = matafuegos._meta.get_field('patente').verbose_name
        self.assertEquals(field_label,'Patente')

    def test_direccion_label(self):
        matafuegos=Matafuegos.objects.get(id=1)
        field_label = matafuegos._meta.get_field('direccion').verbose_name
        self.assertEquals(field_label,'Direccion')

    def test_localizacion_label(self):
        matafuegos=Matafuegos.objects.get(id=1)
        field_label = matafuegos._meta.get_field('localizacion').verbose_name
        self.assertEquals(field_label,'Localizacion')

    def test_numero_localizacion_label(self):
        matafuegos=Matafuegos.objects.get(id=1)
        field_label = matafuegos._meta.get_field('numero_localizacion').verbose_name
        self.assertEquals(field_label,'Numero de localizacion')

    def test_marca_label(self):
        matafuegos=Matafuegos.objects.get(id=1)
        field_label = matafuegos._meta.get_field('marca').verbose_name
        self.assertEquals(field_label,'Marca')

    def test_tipo_label(self):
        matafuegos=Matafuegos.objects.get(id=1)
        field_label = matafuegos._meta.get_field('tipo').verbose_name
        self.assertEquals(field_label,'Tipo')

    def test_categoria_label(self):
        matafuegos=Matafuegos.objects.get(id=1)
        field_label = matafuegos._meta.get_field('categoria').verbose_name
        self.assertEquals(field_label,'Categoria')

    def test_fecha_fabricacion_label(self):
        matafuegos=Matafuegos.objects.get(id=1)
        field_label = matafuegos._meta.get_field('fecha_fabricacion').verbose_name
        self.assertEquals(field_label,'Fecha de fabricacion')

    def test_fecha_carga_label(self):
        matafuegos=Matafuegos.objects.get(id=1)
        field_label = matafuegos._meta.get_field('fecha_carga').verbose_name
        self.assertEquals(field_label,'Fecha de carga')

    def test_fecha_proxima_carga_label(self):
        matafuegos=Matafuegos.objects.get(id=1)
        field_label = matafuegos._meta.get_field('fecha_proxima_carga').verbose_name
        self.assertEquals(field_label,'Fecha de proxima carga')

    def test_fecha_ph_label(self):
        matafuegos=Matafuegos.objects.get(id=1)
        field_label = matafuegos._meta.get_field('fecha_ph').verbose_name
        self.assertEquals(field_label,'Fecha de PH')

    def test_fecha_proxima_ph_label(self):
        matafuegos=Matafuegos.objects.get(id=1)
        field_label = matafuegos._meta.get_field('fecha_proxima_ph').verbose_name
        self.assertEquals(field_label,'Fecha de proxima PH')

    def test_vencido_label(self):
        matafuegos=Matafuegos.objects.get(id=1)
        field_label = matafuegos._meta.get_field('vencido').verbose_name
        self.assertEquals(field_label,'Vencido')

    # LONGITUD -------------------------------------------------------------------------------------------------

    def test_patente_length(self):
        matafuegos=Matafuegos.objects.get(id=1)
        max_length = matafuegos._meta.get_field('patente').max_length
        self.assertEquals(max_length,19)

    def test_direccion_length(self):
        matafuegos=Matafuegos.objects.get(id=1)
        max_length = matafuegos._meta.get_field('direccion').max_length
        self.assertEquals(max_length,30)

    def test_localizacion_length(self):
        matafuegos=Matafuegos.objects.get(id=1)
        max_length = matafuegos._meta.get_field('localizacion').max_length
        self.assertEquals(max_length,100)

    def test_categoria_length(self):
        matafuegos=Matafuegos.objects.get(id=1)
        max_length = matafuegos._meta.get_field('categoria').max_length
        self.assertEquals(max_length,20)

    # FUNCION CALCULAR FECHA -----------------------------------------------------------------------------------

    def test_calcular_fecha(self):
        matafuegos=Matafuegos.objects.get(id=1)
        tipo = TipoMatafuegos.objects.get(id=1)
        self.assertEqual(matafuegos.calcularFecha(matafuegos.fecha_ph,tipo.vencimiento_ph ), date(2022,5,18))
        self.assertEqual(matafuegos.calcularFecha(matafuegos.fecha_carga,tipo.vencimiento_carga), date(2022,5,8))

    def test_save(self):
        matafuegos=Matafuegos.objects.get(id=1)
        self.assertEqual(matafuegos.fecha_proxima_ph, date(2022,5,18))
        self.assertEqual(matafuegos.fecha_proxima_carga, date(2022,5,8))

    # CONTROL DE NUMEROS ---------------------------------------------------------------------------------------

    def test_validar_numero(self):
        m = Matafuegos(numero = -987,
                      numero_dps = 'd8',
                      cliente = Cliente.objects.first(),
                      direccion = 'chacabuco 1147',
                      marca = MarcaMatafuegos.objects.first(),
                      tipo = TipoMatafuegos.objects.first(),
                      categoria = 'd',
                      fecha_fabricacion = date(2022,4,28),
                      fecha_carga = date(2022,4,28),
                      fecha_ph = date(2022,4,28))

        with self.assertRaises(ValidationError) as e:
            m.clean()
        self.assertEqual("['El numero del matafuego debe ser mayor a 0']",str(e.exception))


    def test_validar_numero_interno(self):
        m = Matafuegos(numero = 987,
                      numero_dps = 'd8',
                      numeroInterno = -2,
                      cliente = Cliente.objects.first(),
                      direccion = 'chacabuco 1147',
                      marca = MarcaMatafuegos.objects.first(),
                      tipo = TipoMatafuegos.objects.first(),
                      categoria = 'd',
                      fecha_fabricacion = date(2022,4,28),
                      fecha_carga = date(2022,4,28),
                      fecha_ph = date(2022,4,28))

        with self.assertRaises(ValidationError) as e:
            m.clean()
        self.assertEqual("['El numero interno debe ser mayor a 0']",str(e.exception))


    def test_validar_patente(self):
        m = Matafuegos(numero = 987,
                      numero_dps = 's8',
                      numeroInterno = 2,
                      localizacion = 2,
                      cliente = Cliente.objects.first(),
                      direccion = 'chacabuco 1147',
                      marca = MarcaMatafuegos.objects.first(),
                      tipo = TipoMatafuegos.objects.first(),
                      categoria = 'v',
                      fecha_fabricacion = date(2022,4,28),
                      fecha_carga = date(2022,4,28),
                      fecha_ph = date(2022,4,28))
        with self.assertRaises(ValidationError) as e:
            m.clean()
        self.assertEqual("['Debe especificar la patente del vehiculo']",str(e.exception))

    def test_fecha_fabricacion(self):
        m = Matafuegos(numero = 987,
                      numero_dps = 's8',
                      numeroInterno = 2,
                      localizacion = 2,
                      cliente = Cliente.objects.first(),
                      direccion = 'chacabuco 1147',
                      marca = MarcaMatafuegos.objects.first(),
                      tipo = TipoMatafuegos.objects.first(),
                      categoria = 'd',
                      fecha_fabricacion = date(3000,4,28),
                      fecha_carga = date(2022,4,28),
                      fecha_ph = date(2022,4,28))
        with self.assertRaises(ValidationError) as e:
            m.clean()
        self.assertEqual("['La fecha de fabicacion tiene que ser anterior o igual a la fecha de hoy']",str(e.exception))

    def test_fecha_carga_hoy(self):
        m = Matafuegos(numero = 987,
                      numero_dps = 's8',
                      numeroInterno = 2,
                      localizacion = 2,
                      cliente = Cliente.objects.first(),
                      direccion = 'chacabuco 1147',
                      marca = MarcaMatafuegos.objects.first(),
                      tipo = TipoMatafuegos.objects.first(),
                      categoria = 'd',
                      fecha_fabricacion = date(2022,9,5),
                      fecha_carga = date(3000,4,28),
                      fecha_ph = date(2022,4,28))
        with self.assertRaises(ValidationError) as e:
            m.clean()
        self.assertEqual("['La fecha de carga tiene que ser anterior o igual a la fecha de hoy']",str(e.exception))

    def test_fecha_ph_hoy(self):
        m = Matafuegos(numero = 987,
                      numero_dps = 's8',
                      numeroInterno = 2,
                      localizacion = 2,
                      cliente = Cliente.objects.first(),
                      direccion = 'chacabuco 1147',
                      marca = MarcaMatafuegos.objects.first(),
                      tipo = TipoMatafuegos.objects.first(),
                      categoria = 'd',
                      fecha_fabricacion = date(2022,9,5),
                      fecha_carga = date(2022,4,28),
                      fecha_ph = date(3000,4,28))
        with self.assertRaises(ValidationError) as e:
            m.clean()
        self.assertEqual("['La fecha de ph tiene que ser anterior o igual a la fecha de hoy']",str(e.exception))

    def test_fecha_carga_fabricacion(self):
        m = Matafuegos(numero = 987,
                      numero_dps = 's8',
                      numeroInterno = 2,
                      localizacion = 2,
                      cliente = Cliente.objects.first(),
                      direccion = 'chacabuco 1147',
                      marca = MarcaMatafuegos.objects.first(),
                      tipo = TipoMatafuegos.objects.first(),
                      categoria = 'd',
                      fecha_fabricacion = date(2022,9,3),
                      fecha_carga = date(2022,9,5),
                      fecha_ph = date(2022,4,28))
        with self.assertRaises(ValidationError) as e:
            m.clean()
        self.assertEqual("['La fecha de carga tiene que ser anterior o igual a la fecha de fabricacion']",str(e.exception))

    #Chequear
    def test_fecha_carga_fabricacion(self):
        m = Matafuegos(numero = 987,
                      numero_dps = 's8',
                      numeroInterno = 2,
                      localizacion = 2,
                      cliente = Cliente.objects.first(),
                      direccion = 'chacabuco 1147',
                      marca = MarcaMatafuegos.objects.first(),
                      tipo = TipoMatafuegos.objects.first(),
                      categoria = 'd',
                      fecha_fabricacion = date(2022,3,3),
                      fecha_carga = date(2022,2,5),
                      fecha_ph = date(2022,4,28))
        with self.assertRaises(ValidationError) as e:
            m.clean()
        self.assertEqual("['La fecha de carga tiene que ser anterior o igual a la fecha de fabricacion']",str(e.exception))

    # CATEGORIA DE MATAFUEGOS

    # ETIQUETAS ------------------------------------------------------------------------------------------------

    def test_nombre_label(self):
        categoria = CategoriaMatafuegos.objects.get(id=1)
        field_label = categoria._meta.get_field('nombre').verbose_name
        self.assertEquals(field_label,'Nombre')

    # LONGITUD -------------------------------------------------------------------------------------------------

    def test_nombre_length(self):
        categoria = CategoriaMatafuegos.objects.get(id=1)
        max_length = categoria._meta.get_field('nombre').max_length
        self.assertEquals(max_length,20)

    # TIPO DE MATAFUEGOS

    # ETIQUETAS ------------------------------------------------------------------------------------------------

    def test_tipo_label(self):
        tipo = TipoMatafuegos.objects.get(id=1)
        field_label = tipo._meta.get_field('tipo').verbose_name
        self.assertEquals(field_label,'Tipo')

    def test_categoria_label(self):
        tipo = TipoMatafuegos.objects.get(id=1)
        field_label = tipo._meta.get_field('categoria').verbose_name
        self.assertEquals(field_label,'Categoria')

    def test_vencimiento_carga_label(self):
        tipo = TipoMatafuegos.objects.get(id=1)
        field_label = tipo._meta.get_field('vencimiento_carga').verbose_name
        self.assertEquals(field_label,'Vencimiento de carga')

    def test_vencimeinto_ph_label(self):
        tipo = TipoMatafuegos.objects.get(id=1)
        field_label = tipo._meta.get_field('vencimiento_ph').verbose_name
        self.assertEquals(field_label,'Vencimiento de PH')

    def test_volumen_label(self):
        tipo = TipoMatafuegos.objects.get(id=1)
        field_label = tipo._meta.get_field('volumen').verbose_name
        self.assertEquals(field_label,'Volumen')

    def test_peso_label(self):
        tipo = TipoMatafuegos.objects.get(id=1)
        field_label = tipo._meta.get_field('peso').verbose_name
        self.assertEquals(field_label,'Peso')

    # LONGITUD -------------------------------------------------------------------------------------------------

    def test_nombre_length(self):
        tipo = TipoMatafuegos.objects.get(id=1)
        max_length = tipo._meta.get_field('tipo').max_length
        self.assertEquals(max_length,20)

    #if self.vencimiento_carga:
    #    if self.vencimiento_carga<0:
    #        raise ValidationError('El numero de dias de vencimeinto de carga debe ser mayor a 0')

    def test_vencimiento_carga(self):
        m = TipoMatafuegos(tipo = 'tipo 1',
                         vencimiento_carga = -10,
                         vencimiento_ph = 20,
                         volumen = 5.5,
                         peso = 10)
        with self.assertRaises(ValidationError) as e:
            m.clean()
        self.assertEqual("['El numero de dias de vencimeinto de carga debe ser mayor a 0']",str(e.exception))

    #if self.vencimiento_ph:
    #    if self.vencimiento_ph<0:
    #        raise ValidationError('El numero de dias de vencimeinto de ph debe ser mayor a 0')

    def test_vencimiento_ph(self):
        m = TipoMatafuegos(tipo = 'tipo 1',
                         vencimiento_carga = 10,
                         vencimiento_ph = -20,
                         volumen = 5.5,
                         peso = 10)
        with self.assertRaises(ValidationError) as e:
            m.clean()
        self.assertEqual("['El numero de dias de vencimeinto de ph debe ser mayor a 0']",str(e.exception))

    #if self.volumen:
    #    if self.volumen<0:
    #        raise ValidationError('El volumen debe ser mayor a 0')

    def test_volumen(self):
        m = TipoMatafuegos(tipo = 'tipo 1',
                         vencimiento_carga = 10,
                         vencimiento_ph = 20,
                         volumen = -5.5,
                         peso = 10)
        with self.assertRaises(ValidationError) as e:
            m.clean()
        self.assertEqual("['El volumen debe ser mayor a 0']",str(e.exception))

    #if self.peso:
    #    if self.peso<0:
    #        raise ValidationError('El peso debe ser mayor a 0')

    def test_volumen(self):
        m = TipoMatafuegos(tipo = 'tipo 1',
                         vencimiento_carga = 10,
                         vencimiento_ph = 20,
                         volumen = 5.5,
                         peso = -10)
        with self.assertRaises(ValidationError) as e:
            m.clean()
        self.assertEqual("['El peso debe ser mayor a 0']",str(e.exception))


    # MARCA DE MATAFUEGOS

    # ETIQUETAS ------------------------------------------------------------------------------------------------

    def test_nombre_label(self):
        marca = MarcaMatafuegos.objects.get(id=1)
        field_label = marca._meta.get_field('nombre').verbose_name
        self.assertEquals(field_label,'Nombre')

    # LONGITUD -------------------------------------------------------------------------------------------------

    def test_nombre_length(self):
        marca = MarcaMatafuegos.objects.get(id=1)
        max_length = marca._meta.get_field('nombre').max_length
        self.assertEquals(max_length,15)

"""
    def test_nombre_length(self):
        categoria = CategoriaMatafuegos.objects.get(id=1)
        max_length = categoria._meta.get_field('nombre').max_length
        self.assertEquals(max_length,20)
"""
"""
    def setUp(self):
        print("setUp: Run once for every test method to setup clean data.")
        pass
    def test_false_is_false(self):
        print("Method: test_false_is_false.")
        self.assertFalse(False)

    def test_false_is_true(self):
        print("Method: test_false_is_true.")
        self.assertTrue(False)

    def test_one_plus_one_equals_two(self):
        print("Method: test_one_plus_one_equals_two.")
        self.assertEqual(1 + 1, 2)
"""
