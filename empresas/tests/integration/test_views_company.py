from django.contrib.auth import get_user_model
from django.core import mail
from django.test import TestCase
from django.urls import reverse

from accounts.models import Role
from empresas.models import Company
from empresas.tests.factories import CompanyFactory

User = get_user_model()


class CompanyAdminPanelTests(TestCase):
    def setUp(self):
        self.superuser = User.objects.create_superuser(
            username='super', email='super@example.com', password='testpass123',
        )
        self.client.force_login(self.superuser)

    def test_company_list_renders(self):
        CompanyFactory(nombre='Coopagro Tandil')

        response = self.client.get(reverse('empresas:company-list'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Coopagro Tandil')

    def test_company_create_creates_company_and_admin_user(self):
        response = self.client.post(reverse('empresas:company-create'), {
            'nombre': 'Nueva Cooperativa',
            'admin_username': 'nueva_admin',
            'admin_email': 'admin@nueva.example.com',
            'veh_prefijo': 'V', 'veh_inicio': 1, 'veh_fin': 999, 'veh_actual': 1,
            'dom_prefijo': 'D', 'dom_inicio': 1, 'dom_fin': 999, 'dom_actual': 1,
        })

        self.assertEqual(response.status_code, 302)
        company = Company.objects.get(nombre='Nueva Cooperativa')
        admin_user = User.objects.get(username='nueva_admin')
        self.assertEqual(admin_user.company_id, company.pk)
        self.assertEqual(admin_user.role, Role.ADMIN_EMPRESA)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('admin@nueva.example.com', mail.outbox[0].to)

    def test_company_create_rejects_existing_admin_username(self):
        User.objects.create_user(
            username='admin_existente', password='testpass123',
        )

        response = self.client.post(reverse('empresas:company-create'), {
            'nombre': 'Nueva Cooperativa',
            'admin_username': 'admin_existente',
            'admin_email': 'admin@nueva.example.com',
            'veh_prefijo': 'V', 'veh_inicio': 1, 'veh_fin': 999, 'veh_actual': 1,
            'dom_prefijo': 'D', 'dom_inicio': 1, 'dom_fin': 999, 'dom_actual': 1,
        })

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            'Ya existe un usuario con este nombre de usuario.',
        )
        self.assertFalse(Company.objects.filter(nombre='Nueva Cooperativa').exists())


class CompanyProfileTests(TestCase):
    def setUp(self):
        self.company = CompanyFactory()
        self.admin_user = User.objects.create_user(
            username='empresa_admin', password='testpass123',
            company=self.company, role=Role.ADMIN_EMPRESA,
        )
        self.client.force_login(self.admin_user)

    def test_company_profile_updates_own_company(self):
        response = self.client.post(reverse('empresas:company-profile'), {
            'nombre': 'Nombre actualizado',
            'veh_prefijo': 'V', 'veh_inicio': 1, 'veh_fin': 999, 'veh_actual': 1,
            'dom_prefijo': 'D', 'dom_inicio': 1, 'dom_fin': 999, 'dom_actual': 1,
            'smtp_email': '', 'smtp_password': '',
        })

        self.assertEqual(response.status_code, 302)
        self.company.refresh_from_db()
        self.assertEqual(self.company.nombre, 'Nombre actualizado')

    def test_company_profile_updates_dps_numbering(self):
        response = self.client.post(reverse('empresas:company-profile'), {
            'nombre': self.company.nombre,
            'veh_prefijo': 'VX', 'veh_inicio': 10, 'veh_fin': 500, 'veh_actual': 20,
            'dom_prefijo': 'DX', 'dom_inicio': 5, 'dom_fin': 300, 'dom_actual': 15,
            'smtp_email': '', 'smtp_password': '',
        })

        self.assertEqual(response.status_code, 302)
        self.company.refresh_from_db()
        self.assertEqual(self.company.veh_prefijo, 'VX')
        self.assertEqual(self.company.veh_inicio, 10)
        self.assertEqual(self.company.veh_fin, 500)
        self.assertEqual(self.company.veh_actual, 20)
        self.assertEqual(self.company.dom_prefijo, 'DX')
        self.assertEqual(self.company.dom_inicio, 5)
        self.assertEqual(self.company.dom_fin, 300)
        self.assertEqual(self.company.dom_actual, 15)

    def test_company_profile_updates_numero_recargador(self):
        response = self.client.post(reverse('empresas:company-profile'), {
            'nombre': self.company.nombre,
            'numero_recargador': '150',
            'veh_prefijo': 'V', 'veh_inicio': 1, 'veh_fin': 999, 'veh_actual': 1,
            'dom_prefijo': 'D', 'dom_inicio': 1, 'dom_fin': 999, 'dom_actual': 1,
            'smtp_email': '', 'smtp_password': '',
        })

        self.assertEqual(response.status_code, 302)
        self.company.refresh_from_db()
        self.assertEqual(self.company.numero_recargador, '150')

    def test_company_profile_cannot_deactivate_company(self):
        response = self.client.post(reverse('empresas:company-profile'), {
            'nombre': self.company.nombre,
            'is_active': False,
            'veh_prefijo': 'V', 'veh_inicio': 1, 'veh_fin': 999, 'veh_actual': 1,
            'dom_prefijo': 'D', 'dom_inicio': 1, 'dom_fin': 999, 'dom_actual': 1,
            'smtp_email': '', 'smtp_password': '',
        })

        self.assertEqual(response.status_code, 302)
        self.company.refresh_from_db()
        self.assertTrue(self.company.is_active)
