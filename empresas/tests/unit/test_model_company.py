from django.test import TestCase

from empresas.tests.factories import CompanyFactory


class CompanyModelTests(TestCase):
    def test_str_returns_nombre(self):
        company = CompanyFactory(nombre='Coopagro Tandil')
        self.assertEqual(str(company), 'Coopagro Tandil')

    def test_is_active_defaults_to_true(self):
        company = CompanyFactory()
        self.assertTrue(company.is_active)

    def test_has_audit_fields(self):
        company = CompanyFactory()
        self.assertIsNotNone(company.created_at)
        self.assertIsNotNone(company.updated_at)
