from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from accounts.models import Role
from cliente.tests.factories import ClienteFactory
from empresas.tests.factories import CompanyFactory
from matafuegos.tests.factories import MatafuegosFactory

User = get_user_model()


class DashboardViewTests(TestCase):
    def test_operador_sees_kpis(self):
        company = CompanyFactory()
        cliente = ClienteFactory(company=company, estado='a')
        MatafuegosFactory(cliente=cliente)
        user = User.objects.create_user(
            username='operador', password='testpass123', company=company, role=Role.OPERADOR,
        )
        self.client.force_login(user)

        response = self.client.get(reverse('dashboard'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['kpi_clientes_activos'], 1)
        self.assertEqual(response.context['kpi_matafuegos_totales'], 1)

    def test_raiz_redirects_superuser_to_company_list(self):
        superuser = User.objects.create_superuser(username='super', email='s@example.com', password='testpass123')
        self.client.force_login(superuser)

        response = self.client.get(reverse('raiz'))

        self.assertRedirects(response, reverse('empresas:company-list'))

    def test_raiz_redirects_company_user_to_dashboard(self):
        company = CompanyFactory()
        user = User.objects.create_user(
            username='operador2', password='testpass123', company=company, role=Role.OPERADOR,
        )
        self.client.force_login(user)

        response = self.client.get(reverse('raiz'))

        self.assertRedirects(response, reverse('dashboard'))
