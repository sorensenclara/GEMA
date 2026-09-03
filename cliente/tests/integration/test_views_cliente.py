from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from accounts.models import Role
from cliente.models import Cliente
from cliente.tests.factories import ClienteFactory
from empresas.tests.factories import CompanyFactory

User = get_user_model()


class ClienteViewsTests(TestCase):
    def setUp(self):
        self.company = CompanyFactory()
        self.user = User.objects.create_user(
            username='operador', password='testpass123',
            company=self.company, role=Role.OPERADOR,
        )
        self.client.force_login(self.user)

    def test_list_shows_only_company_clientes(self):
        ClienteFactory(company=self.company, nombre='De mi compañía')
        ClienteFactory(nombre='De otra compañía')

        response = self.client.get(reverse('cliente:list'))

        self.assertContains(response, 'De mi compañía')
        self.assertNotContains(response, 'De otra compañía')

    def test_create_cliente(self):
        response = self.client.post(reverse('cliente:create'), {
            'codigo': '1', 'nombre': 'Nuevo Cliente', 'direccion': 'San Lorenzo 516',
            'telefono': '2233445566', 'tipo': 'p', 'estado': 'a',
        })

        self.assertEqual(response.status_code, 302)
        cliente = Cliente.objects.get(codigo='1')
        self.assertEqual(cliente.company_id, self.company.pk)

    def test_toggle_active(self):
        cliente = ClienteFactory(company=self.company, estado='a')

        self.client.post(reverse('cliente:toggle-active', args=[cliente.pk]))

        cliente.refresh_from_db()
        self.assertEqual(cliente.estado, 'i')

    def test_informe_returns_pdf(self):
        cliente = ClienteFactory(company=self.company)

        response = self.client.get(reverse('cliente:informe', args=[cliente.pk]))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')

    def test_enviar_informe_shows_error_without_email(self):
        cliente = ClienteFactory(company=self.company, email='')

        response = self.client.post(reverse('cliente:enviar-informe', args=[cliente.pk]))

        self.assertRedirects(response, reverse('cliente:list'))
