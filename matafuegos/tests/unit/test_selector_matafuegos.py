from datetime import date, timedelta

from django.test import TestCase
from freezegun import freeze_time

from matafuegos.selectors import (
    count_matafuegos,
    count_vencimiento_proximo,
    list_matafuegos,
    list_proximos_vencimientos_carga,
    matafuegos_de_cliente,
)
from matafuegos.tests.factories import MatafuegosFactory
from empresas.tests.factories import CompanyFactory


class ListMatafuegosTests(TestCase):
    def test_only_returns_matafuegos_of_given_company(self):
        company = CompanyFactory()
        mio = MatafuegosFactory(cliente__company=company)
        MatafuegosFactory()

        resultado = list(list_matafuegos(company))

        self.assertEqual(resultado, [mio])

    def test_q_filters_by_numero(self):
        company = CompanyFactory()
        match = MatafuegosFactory(cliente__company=company, numero=555)
        MatafuegosFactory(cliente__company=company, numero=111)

        resultado = list(list_matafuegos(company, q='555'))

        self.assertEqual(resultado, [match])

    def test_tipo_filters_by_tipo(self):
        from matafuegos.tests.factories import TipoMatafuegosFactory

        company = CompanyFactory()
        tipo = TipoMatafuegosFactory()
        match = MatafuegosFactory(cliente__company=company, tipo=tipo)
        MatafuegosFactory(cliente__company=company)

        resultado = list(list_matafuegos(company, tipo=tipo.pk))

        self.assertEqual(resultado, [match])

    def test_estado_filters_by_estado(self):
        company = CompanyFactory()
        activo = MatafuegosFactory(cliente__company=company, estado='a')
        MatafuegosFactory(cliente__company=company, estado='i')

        resultado = list(list_matafuegos(company, estado='a'))

        self.assertEqual(resultado, [activo])

    def test_vencido_filters_by_vencido(self):
        company = CompanyFactory()
        vencido = MatafuegosFactory(cliente__company=company, vencido=True)
        MatafuegosFactory(cliente__company=company, vencido=False)

        resultado = list(list_matafuegos(company, vencido='1'))

        self.assertEqual(resultado, [vencido])

    def test_vencido_0_filters_no_vencidos(self):
        company = CompanyFactory()
        no_vencido = MatafuegosFactory(cliente__company=company, vencido=False)
        MatafuegosFactory(cliente__company=company, vencido=True)

        resultado = list(list_matafuegos(company, vencido='0'))

        self.assertEqual(resultado, [no_vencido])


class CountMatafuegosTests(TestCase):
    def test_counts_only_matafuegos_of_company(self):
        company = CompanyFactory()
        MatafuegosFactory(cliente__company=company)
        MatafuegosFactory(cliente__company=company)
        MatafuegosFactory()

        self.assertEqual(count_matafuegos(company), 2)


class VencimientoProximoTests(TestCase):
    @freeze_time('2024-01-01')
    def test_list_proximos_vencimientos_carga_within_window(self):
        company = CompanyFactory()
        dentro = MatafuegosFactory(cliente__company=company, fecha_carga=date(2024, 1, 1), tipo__vencimiento_carga=10)
        fuera = MatafuegosFactory(cliente__company=company, fecha_carga=date(2024, 1, 1), tipo__vencimiento_carga=200)

        resultado = list(list_proximos_vencimientos_carga(company, dias=30))

        self.assertIn(dentro, resultado)
        self.assertNotIn(fuera, resultado)

    @freeze_time('2024-01-01')
    def test_count_vencimiento_proximo(self):
        company = CompanyFactory()
        MatafuegosFactory(cliente__company=company, fecha_carga=date(2024, 1, 1), tipo__vencimiento_carga=10)

        self.assertEqual(count_vencimiento_proximo(company, dias=30), 1)


class MatafuegosDeClienteTests(TestCase):
    def test_returns_matafuegos_of_given_cliente(self):
        matafuego = MatafuegosFactory()
        MatafuegosFactory()

        resultado = list(matafuegos_de_cliente(matafuego.cliente))

        self.assertEqual(resultado, [matafuego])
