from django.test import TestCase

from empresas.exceptions import RangoDpsAgotadoException
from empresas.services import incrementar_dps
from empresas.tests.factories import CompanyFactory


class IncrementarDpsTests(TestCase):
    def test_returns_prefixed_current_value_and_advances_counter(self):
        company = CompanyFactory(veh_prefijo='V', veh_actual=10, veh_fin=999)

        valor = incrementar_dps(company, 'veh', paso=2)

        self.assertEqual(valor, 'V10')
        company.refresh_from_db()
        self.assertEqual(company.veh_actual, 12)

    def test_raises_when_range_is_exhausted(self):
        company = CompanyFactory(veh_prefijo='V', veh_actual=998, veh_fin=999)

        with self.assertRaises(RangoDpsAgotadoException):
            incrementar_dps(company, 'veh', paso=2)

    def test_unlimited_range_when_fin_is_zero(self):
        company = CompanyFactory(veh_prefijo='V', veh_actual=0, veh_fin=0)

        valor = incrementar_dps(company, 'veh', paso=2)

        self.assertEqual(valor, 'V0')
