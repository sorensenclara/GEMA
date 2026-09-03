from datetime import date

from django.core.exceptions import ValidationError
from django.test import TestCase

from matafuegos.models import Matafuegos
from matafuegos.tests.factories import MarcaMatafuegosFactory, MatafuegosFactory, TipoMatafuegosFactory
from cliente.tests.factories import ClienteFactory


class MatafuegosFieldsTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.matafuego = MatafuegosFactory()

    def test_field_labels(self):
        labels = {
            'numero': 'Numero',
            'numeroInterno': 'Numero interno',
            'numero_dps': 'Numero de DPS',
            'cliente': 'Cliente',
            'patente': 'Patente',
            'direccion': 'Direccion',
            'localizacion': 'Localizacion',
            'numero_localizacion': 'Numero de localizacion',
            'marca': 'Marca',
            'tipo': 'Tipo',
            'categoria': 'Categoria',
            'fecha_fabricacion': 'Fecha de fabricacion',
            'fecha_carga': 'Fecha de carga',
            'fecha_proxima_carga': 'Fecha de proxima carga',
            'fecha_ph': 'Fecha de PH',
            'fecha_proxima_ph': 'Fecha de proxima PH',
            'vencido': 'Vencido',
        }
        for field_name, expected in labels.items():
            with self.subTest(field=field_name):
                self.assertEqual(self.matafuego._meta.get_field(field_name).verbose_name, expected)

    def test_field_max_lengths(self):
        max_lengths = {'patente': 19, 'direccion': 30, 'localizacion': 100, 'categoria': 20}
        for field_name, expected in max_lengths.items():
            with self.subTest(field=field_name):
                self.assertEqual(self.matafuego._meta.get_field(field_name).max_length, expected)

    def test_str_includes_numero_and_tipo(self):
        matafuego = MatafuegosFactory(numero=987)
        self.assertEqual(str(matafuego), f'987-{matafuego.tipo}')


class MatafuegosCalcularFechaTests(TestCase):
    def test_calcular_fecha_adds_days(self):
        matafuego = MatafuegosFactory(fecha_carga=date(2022, 4, 28), fecha_ph=date(2022, 4, 28))
        tipo = matafuego.tipo
        self.assertEqual(matafuego.calcularFecha(matafuego.fecha_ph, tipo.vencimiento_ph), date(2022, 5, 18))
        self.assertEqual(matafuego.calcularFecha(matafuego.fecha_carga, tipo.vencimiento_carga), date(2022, 5, 8))


class MatafuegosSaveTests(TestCase):
    def test_save_computes_fechas_proximas(self):
        matafuego = MatafuegosFactory(fecha_carga=date(2022, 4, 28), fecha_ph=date(2022, 4, 28))
        self.assertEqual(matafuego.fecha_proxima_ph, date(2022, 5, 18))
        self.assertEqual(matafuego.fecha_proxima_carga, date(2022, 5, 8))

    def test_save_sets_patente_for_maquinaria_agricola(self):
        matafuego = MatafuegosFactory(categoria='ma', patente=None)
        self.assertEqual(matafuego.patente, 'Maquina agricola')


class MatafuegosValidationTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.cliente = ClienteFactory()
        cls.marca = MarcaMatafuegosFactory()
        cls.tipo = TipoMatafuegosFactory()

    def _matafuego(self, **overrides):
        defaults = dict(
            numero=987, numero_dps='d8', cliente=self.cliente, direccion='chacabuco 1147',
            marca=self.marca, tipo=self.tipo, categoria='d',
            fecha_fabricacion=date(2022, 4, 28), fecha_carga=date(2022, 4, 28), fecha_ph=date(2022, 4, 28),
        )
        defaults.update(overrides)
        return Matafuegos(**defaults)

    def test_numero_must_be_positive(self):
        m = self._matafuego(numero=-987)
        with self.assertRaises(ValidationError) as ctx:
            m.clean()
        self.assertEqual("['El numero del matafuego debe ser mayor a 0']", str(ctx.exception))

    def test_numero_interno_must_be_positive(self):
        m = self._matafuego(numeroInterno=-2)
        with self.assertRaises(ValidationError) as ctx:
            m.clean()
        self.assertEqual("['El numero interno debe ser mayor a 0']", str(ctx.exception))

    def test_patente_required_for_categoria_vehicular(self):
        m = self._matafuego(categoria='v', patente=None)
        with self.assertRaises(ValidationError) as ctx:
            m.clean()
        self.assertEqual("['Debe especificar la patente del vehiculo']", str(ctx.exception))

    def test_fecha_fabricacion_no_puede_ser_futura(self):
        m = self._matafuego(fecha_fabricacion=date(3000, 4, 28))
        with self.assertRaises(ValidationError) as ctx:
            m.clean()
        self.assertEqual("['La fecha de fabicacion tiene que ser anterior o igual a la fecha de hoy']", str(ctx.exception))

    def test_fecha_carga_no_puede_ser_futura(self):
        m = self._matafuego(fecha_fabricacion=date(2022, 9, 5), fecha_carga=date(3000, 4, 28))
        with self.assertRaises(ValidationError) as ctx:
            m.clean()
        self.assertEqual("['La fecha de carga tiene que ser anterior o igual a la fecha de hoy']", str(ctx.exception))

    def test_fecha_ph_no_puede_ser_futura(self):
        m = self._matafuego(fecha_fabricacion=date(2022, 9, 5), fecha_carga=date(2022, 4, 28), fecha_ph=date(3000, 4, 28))
        with self.assertRaises(ValidationError) as ctx:
            m.clean()
        self.assertEqual("['La fecha de ph tiene que ser anterior o igual a la fecha de hoy']", str(ctx.exception))

    def test_fecha_carga_no_puede_ser_anterior_a_fabricacion(self):
        m = self._matafuego(fecha_fabricacion=date(2022, 9, 3), fecha_carga=date(2022, 2, 5))
        with self.assertRaises(ValidationError) as ctx:
            m.clean()
        self.assertEqual("['La fecha de carga tiene que ser anterior o igual a la fecha de fabricacion']", str(ctx.exception))

    def test_fecha_ph_no_puede_ser_anterior_a_fabricacion(self):
        m = self._matafuego(fecha_fabricacion=date(2022, 9, 3), fecha_carga=date(2022, 9, 5), fecha_ph=date(2022, 2, 5))
        with self.assertRaises(ValidationError) as ctx:
            m.clean()
        self.assertEqual("['La fecha de ph tiene que ser anterior o igual a la fecha de fabricacion']", str(ctx.exception))
