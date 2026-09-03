from django.test import TestCase

from cliente.selectors import count_clientes_activos, list_clientes
from cliente.tests.factories import ClienteFactory
from empresas.tests.factories import CompanyFactory


class ListClientesTests(TestCase):
    def test_only_returns_clientes_of_given_company(self):
        company = CompanyFactory()
        ClienteFactory(company=company, nombre='De mi compañía')
        ClienteFactory(nombre='De otra compañía')

        resultado = list_clientes(company)

        self.assertEqual(list(resultado), list(company.clientes.all()))
        self.assertEqual(resultado.count(), 1)

    def test_q_filters_by_nombre_codigo_or_cuit(self):
        company = CompanyFactory()
        match = ClienteFactory(company=company, nombre='Ferretería Central', codigo='100')
        ClienteFactory(company=company, nombre='Otro Cliente', codigo='200')

        resultado = list_clientes(company, q='Central')

        self.assertEqual(list(resultado), [match])


class CountClientesActivosTests(TestCase):
    def test_counts_only_active_clientes_of_company(self):
        company = CompanyFactory()
        ClienteFactory(company=company, estado='a')
        ClienteFactory(company=company, estado='a')
        ClienteFactory(company=company, estado='i')

        self.assertEqual(count_clientes_activos(company), 2)
