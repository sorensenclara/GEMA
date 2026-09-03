from django.core import mail
from django.test import TestCase
from django.urls import reverse

from accounts.models import Role, User
from accounts.tests.factories import UserFactory
from empresas.tests.factories import CompanyFactory


class UserManagementTests(TestCase):
    def setUp(self):
        self.company = CompanyFactory()
        self.admin = UserFactory(company=self.company, role=Role.ADMIN_EMPRESA)
        self.client.force_login(self.admin)

    def test_user_list_shows_only_company_users(self):
        UserFactory(company=self.company, username='de_mi_empresa')
        UserFactory(username='de_otra_empresa')

        response = self.client.get(reverse('accounts:user-list'))

        self.assertContains(response, 'de_mi_empresa')
        self.assertNotContains(response, 'de_otra_empresa')

    def test_create_user_sends_invitation(self):
        response = self.client.post(reverse('accounts:user-create'), {
            'username': 'nuevo_operador',
            'first_name': '', 'last_name': '',
            'email': 'nuevo@example.com',
            'role': Role.OPERADOR,
            'cliente': '',
        })

        self.assertEqual(response.status_code, 302)
        user = User.objects.get(username='nuevo_operador')
        self.assertEqual(user.company_id, self.company.pk)
        self.assertEqual(len(mail.outbox), 1)

    def test_cannot_deactivate_self(self):
        response = self.client.post(reverse('accounts:user-toggle-active', args=[self.admin.pk]))

        self.assertRedirects(response, reverse('accounts:user-list'))
        self.admin.refresh_from_db()
        self.assertTrue(self.admin.is_active)

    def test_can_deactivate_another_user(self):
        other = UserFactory(company=self.company)

        self.client.post(reverse('accounts:user-toggle-active', args=[other.pk]))

        other.refresh_from_db()
        self.assertFalse(other.is_active)
