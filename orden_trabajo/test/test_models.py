from datetime import date

from django.core.exceptions import ValidationError
from django.test import TestCase

from orden_trabajo.models import Tarea, Ordenes_de_trabajo, TareaOrden

from cliente.models import Cliente

from empresas.models import Company

from matafuegos.models import MarcaMatafuegos, CategoriaMatafuegos, TipoMatafuegos, Matafuegos


class TareaTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        #Set up non-modified objects used by all test methods
        company = Company.objects.create(nombre='Compañía de prueba')
        Tarea.objects.create(id=1, company=company, nombre='limpiar', precio=100)

    def test_nombre_label(self):
        tarea = Tarea.objects.get(id=1)
        field_label = tarea._meta.get_field('nombre').verbose_name
        self.assertEquals(field_label,'Nombre')

    def test_nombre_max_length(self):
        tarea = Tarea.objects.get(id=1)
        max_length = tarea._meta.get_field('nombre').max_length
        self.assertEquals(max_length,120)

    def test_precio_label(self):
        tarea = Tarea.objects.get(id=1)
        field_label = tarea._meta.get_field('precio').verbose_name
        self.assertEquals(field_label,'Precio')

    def test_precio(self):
        t = Tarea(id=1,nombre='limpiar', precio=-100)
        with self.assertRaises(ValidationError) as e:
            t.clean()
        self.assertEqual("['El precio debe ser mayor a 0']",str(e.exception))

class OrdenesTrabajoTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        #Set up non-modified objects used by all test methods
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

        matafuegos = Matafuegos.objects.create(company = company,
                                  numero = 987,
                                  numero_dps = 's8',
                                  cliente = cliente,
                                  direccion = 'chacabuco 1147',
                                  marca = marca,
                                  tipo = tipo,
                                  categoria = 'Domiciliario',
                                  fecha_fabricacion = date(2022,4,28),
                                  fecha_carga = date(2022,4,28),
                                  fecha_ph = date(2022,4,28))

        orden = Ordenes_de_trabajo.objects.create(company= company, fecha_creacion= date(2022,4,26), fecha_entrega=date(2022,4,28), fecha_cierre= date(2022,4,28), cliente= cliente, estado= 'p', matafuegos= matafuegos)

        t1= Tarea.objects.create(company=company, nombre='limpieza', precio='100')
        TareaOrden.objects.create(tarea=t1, orden=orden)
        t2= Tarea.objects.create(company=company, nombre='reparacion', precio='200')
        TareaOrden.objects.create(tarea=t2, orden=orden)

    pass

    def test_fecha_creacion_label(self):
        orden = Ordenes_de_trabajo.objects.get(id=1)
        field_label = orden._meta.get_field('fecha_creacion').verbose_name
        self.assertEquals(field_label,'Fecha de creacion de orden')

    def test_fecha_inicio_label(self):
        orden = Ordenes_de_trabajo.objects.get(id=1)
        field_label = orden._meta.get_field('fecha_inicio').verbose_name
        self.assertEquals(field_label,'Fecha de inicio')

    def test_fecha_entrega_label(self):
        orden = Ordenes_de_trabajo.objects.get(id=1)
        field_label = orden._meta.get_field('fecha_entrega').verbose_name
        self.assertEquals(field_label,'Entrega estimada')

    def test_fecha_cierre_label(self):
        orden = Ordenes_de_trabajo.objects.get(id=1)
        field_label = orden._meta.get_field('fecha_cierre').verbose_name
        self.assertEquals(field_label,'Fecha de cierre')

    def test_cliente_label(self):
        orden = Ordenes_de_trabajo.objects.get(id=1)
        field_label = orden._meta.get_field('cliente').verbose_name
        self.assertEquals(field_label,'Cliente')

    def test_matafuegos_label(self):
        orden = Ordenes_de_trabajo.objects.get(id=1)
        field_label = orden._meta.get_field('matafuegos').verbose_name
        self.assertEquals(field_label,'Matafuegos')

    def test_estado_label(self):
        orden = Ordenes_de_trabajo.objects.get(id=1)
        field_label = orden._meta.get_field('estado').verbose_name
        self.assertEquals(field_label,'Estado')

    def test_estado_max_length(self):
        orden = Ordenes_de_trabajo.objects.get(id=1)
        max_length = orden._meta.get_field('estado').max_length
        self.assertEquals(max_length, 80)

    def test_monto_total_label(self):
        orden = Ordenes_de_trabajo.objects.get(id=1)
        field_label = orden._meta.get_field('monto_total').verbose_name
        self.assertEquals(field_label,'Monto')

    def test_notas_label(self):
        orden = Ordenes_de_trabajo.objects.get(id=1)
        field_label = orden._meta.get_field('notas').verbose_name
        self.assertEquals(field_label,'Notas')

    def test_notas_max_length(self):
        orden = Ordenes_de_trabajo.objects.get(id=1)
        max_length = orden._meta.get_field('notas').max_length
        self.assertEquals(max_length, 80)

    def test_usuario_label(self):
        orden = Ordenes_de_trabajo.objects.get(id=1)
        field_label = orden._meta.get_field('usuario').verbose_name
        self.assertEquals(field_label,'Usuario responsable')

    def test_usuario_max_length(self):
        orden = Ordenes_de_trabajo.objects.get(id=1)
        max_length = orden._meta.get_field('usuario').max_length
        self.assertEquals(max_length, 30)


    """NO VA MAS
    def test_fecha_entrega(self):
        marca = MarcaMatafuegos(nombre = 'abc')

        categoria = CategoriaMatafuegos(nombre = 'categoria 1')

        tipo = TipoMatafuegos(tipo = 'tipo 1',
                             categoria = categoria,
                             vencimiento_carga = 10,
                             vencimiento_ph = 20,
                             volumen = 5.5,
                             peso = 10)

        cliente = Cliente(codigo = 789,
                           cuit_cuil = 987,
                           nombre = 'Victoria Dell Oso',
                           direccion = 'chacabuco 1147',
                           telefono = '2492565089',
                           email = 'maylendelloso@gmail.com',
                           tipo = 'Persona',
                           estado = 'Activo')

        matafuegos = Matafuegos(numero = 987,
                                  numero_dps = 's8',
                                  cliente = cliente,
                                  direccion = 'chacabuco 1147',
                                  marca = marca,
                                  tipo = tipo,
                                  categoria = 'Domiciliario',
                                  fecha_fabricacion = date(2022,4,28),
                                  fecha_carga = date(2022,4,28),
                                  fecha_ph = date(2022,4,28))

        o = Ordenes_de_trabajo(fecha_creacion= date(2022,4,26),
                               fecha_entrega=date(2022,4,28),
                               fecha_cierre= date(2022,4,28),
                               cliente= cliente,
                               estado= 'p',
                               matafuegos= matafuegos)

        with self.assertRaises(ValidationError) as e:
            o.clean()
        self.assertEqual("['La fecha de entrega debe ser posterior o igual a la fecha de hoy']",str(e.exception))
        """
    def test_monto_total(self):
        orden=Ordenes_de_trabajo.objects.get(id=1)
        self.assertEqual(orden.calcular_monto(), 300)


class TareaOrdenTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        #Set up non-modified objects used by all test methods
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

        matafuegos = Matafuegos.objects.create(company = company,
                                  numero = 987,
                                  numero_dps = 's8',
                                  cliente = cliente,
                                  direccion = 'chacabuco 1147',
                                  marca = marca,
                                  tipo = tipo,
                                  categoria = 'Domiciliario',
                                  fecha_fabricacion = date(2022,4,28),
                                  fecha_carga = date(2022,4,28),
                                  fecha_ph = date(2022,4,28))

        tarea= Tarea.objects.create(company=company, nombre='limpieza', precio='100')

        orden= Ordenes_de_trabajo.objects.create(company=company, fecha_creacion= date(2022,4,26), fecha_entrega=date(2022,4,28), fecha_cierre= date(2022,4,28), cliente= cliente, estado= 'p', matafuegos= matafuegos)

        TareaOrden.objects.create(tarea= tarea, orden= orden)
    pass

    def test_tarea_label(self):
        tarea = TareaOrden.objects.first()
        field_label = tarea._meta.get_field('tarea').verbose_name
        self.assertEquals(field_label,'Tarea')

    def test_orden_label(self):
        orden = TareaOrden.objects.first()
        field_label = orden._meta.get_field('orden').verbose_name
        self.assertEquals(field_label,'Orden')

    def test_precioAJ_label(self):
        orden = TareaOrden.objects.first()
        field_label = orden._meta.get_field('precioAj').verbose_name
        self.assertEquals(field_label,'Precio ajustable')

    def test_cant_cargada_label(self):
        orden = TareaOrden.objects.first()
        field_label = orden._meta.get_field('cant_cargada').verbose_name
        self.assertEquals(field_label,'Cantidad cargada')

    def test_precio_aj(self):

        marca = MarcaMatafuegos(nombre = 'abc')

        categoria = CategoriaMatafuegos(nombre = 'categoria 1')

        tipo = TipoMatafuegos(tipo = 'tipo 1',
                                             categoria = categoria,
                                             vencimiento_carga = 10,
                                             vencimiento_ph = 20,
                                             volumen = 5.5,
                                             peso = 10)

        cliente = Cliente(codigo = 789,
                               cuit_cuil = 987,
                               nombre = 'Victoria Dell Oso',
                               direccion = 'chacabuco 1147',
                               telefono = '2492565089',
                               email = 'maylendelloso@gmail.com',
                               tipo = 'Persona',
                               estado = 'Activo')

        matafuegos = Matafuegos(numero = 987,
                                  numero_dps = 's8',
                                  cliente = cliente,
                                  direccion = 'chacabuco 1147',
                                  marca = marca,
                                  tipo = tipo,
                                  categoria = 'Domiciliario',
                                  fecha_fabricacion = date(2022,4,28),
                                  fecha_carga = date(2022,4,28),
                                  fecha_ph = date(2022,4,28))

        tarea= Tarea(nombre='limpieza', precio='100')

        orden= Ordenes_de_trabajo(fecha_creacion= date(2022,4,26), fecha_entrega=date(2022,4,28), fecha_cierre= date(2022,4,28), cliente= cliente, estado= 'p', matafuegos= matafuegos)

        t = TareaOrden(tarea= tarea, orden= orden, precioAj = -2)

        with self.assertRaises(ValidationError) as e:
            t.clean()
        self.assertEqual("['El precio debe ser mayor o igual a 0']",str(e.exception))

    def test_cantidad_cargada(self):

        marca = MarcaMatafuegos(nombre = 'abc')

        categoria = CategoriaMatafuegos(nombre = 'categoria 1')

        tipo = TipoMatafuegos(tipo = 'tipo 1',
                                             categoria = categoria,
                                             vencimiento_carga = 10,
                                             vencimiento_ph = 20,
                                             volumen = 5.5,
                                             peso = 10)

        cliente = Cliente(codigo = 789,
                               cuit_cuil = 987,
                               nombre = 'Victoria Dell Oso',
                               direccion = 'chacabuco 1147',
                               telefono = '2492565089',
                               email = 'maylendelloso@gmail.com',
                               tipo = 'Persona',
                               estado = 'Activo')

        matafuegos = Matafuegos(numero = 987,
                                  numero_dps = 's8',
                                  cliente = cliente,
                                  direccion = 'chacabuco 1147',
                                  marca = marca,
                                  tipo = tipo,
                                  categoria = 'Domiciliario',
                                  fecha_fabricacion = date(2022,4,28),
                                  fecha_carga = date(2022,4,28),
                                  fecha_ph = date(2022,4,28))

        tarea= Tarea(nombre='limpieza', precio='100')

        orden= Ordenes_de_trabajo(fecha_creacion= date(2022,4,26), fecha_entrega=date(2022,4,28), fecha_cierre= date(2022,4,28), cliente= cliente, estado= 'p', matafuegos= matafuegos)

        t = TareaOrden(tarea= tarea, orden= orden, cant_cargada = -2)

        with self.assertRaises(ValidationError) as e:
            t.clean()
        self.assertEqual("['La cantidad debe ser mayor o igual a 0']",str(e.exception))
