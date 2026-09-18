from django.test import TestCase

from empresas.exceptions import NumeracionDpsNoConfiguradaException, RangoDpsAgotadoException
from empresas.services import incrementar_dps
from empresas.tests.factories import CompanyFactory


class IncrementarDpsTests(TestCase):
    def test_returns_prefixed_current_value_and_advances_counter_by_one(self):
        company = CompanyFactory(veh_prefijo='V', veh_actual=10, veh_fin=999)

        valor = incrementar_dps(company, 'veh')

        self.assertEqual(valor, 'V10')
        company.refresh_from_db()
        self.assertEqual(company.veh_actual, 11)

    def test_raises_when_range_is_exhausted(self):
        company = CompanyFactory(veh_prefijo='V', veh_actual=999, veh_fin=999)

        with self.assertRaises(RangoDpsAgotadoException):
            incrementar_dps(company, 'veh')

    def test_raises_when_fin_is_not_configured(self):
        company = CompanyFactory(veh_prefijo='V', veh_actual=0, veh_fin=0)

        with self.assertRaises(NumeracionDpsNoConfiguradaException):
            incrementar_dps(company, 'veh')

    def test_raises_when_prefijo_is_not_configured(self):
        company = CompanyFactory(veh_prefijo='', veh_actual=0, veh_fin=999)

        with self.assertRaises(NumeracionDpsNoConfiguradaException):
            incrementar_dps(company, 'veh')
