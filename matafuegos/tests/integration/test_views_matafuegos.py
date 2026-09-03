from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from accounts.models import Role
from cliente.tests.factories import ClienteFactory
from empresas.tests.factories import CompanyFactory
from matafuegos.models import Matafuegos
from matafuegos.tests.factories import MarcaMatafuegosFactory, MatafuegosFactory, TipoMatafuegosFactory

User = get_user_model()


class MatafuegosViewsTests(TestCase):
    def setUp(self):
        self.company = CompanyFactory()
        self.user = User.objects.create_user(
            username='operador', password='testpass123',
            company=self.company, role=Role.OPERADOR,
        )
        self.client.force_login(self.user)

    def test_list_shows_only_company_matafuegos(self):
        MatafuegosFactory(cliente__company=self.company, numero=1)
        MatafuegosFactory(numero=2)

        response = self.client.get(reverse('matafuegos:list'))

        self.assertEqual(len(response.context['matafuegos']), 1)

    def test_create_matafuego(self):
        cliente = ClienteFactory(company=self.company)
        marca = MarcaMatafuegosFactory()
        tipo = TipoMatafuegosFactory()

        response = self.client.post(reverse('matafuegos:create'), {
            'numero': '1', 'cliente': cliente.pk, 'marca': marca.pk, 'tipo': tipo.pk,
            'categoria': 'd', 'fecha_fabricacion': '2022-04-28',
            'fecha_carga': '2022-04-28', 'fecha_ph': '2022-04-28',
        })

        self.assertEqual(response.status_code, 302)
        matafuego = Matafuegos.objects.get(numero=1)
        self.assertEqual(matafuego.company_id, self.company.pk)

    def test_create_matafuego_vehicular_sin_patente_no_guarda_y_muestra_error(self):
        cliente = ClienteFactory(company=self.company)
        marca = MarcaMatafuegosFactory()
        tipo = TipoMatafuegosFactory()

        response = self.client.post(reverse('matafuegos:create'), {
            'numero': '1', 'cliente': cliente.pk, 'marca': marca.pk, 'tipo': tipo.pk,
            'categoria': 'v', 'patente': '', 'fecha_fabricacion': '2022-04-28',
            'fecha_carga': '2022-04-28', 'fecha_ph': '2022-04-28',
        })

        self.assertEqual(response.status_code, 200)
        self.assertFalse(Matafuegos.objects.filter(numero=1).exists())
        self.assertContains(response, 'Debe especificar la patente del vehiculo')

    def test_vencimientos_view_requires_dates(self):
        response = self.client.post(reverse('matafuegos:vencimientos'), {})
        self.assertRedirects(response, reverse('matafuegos:vencimientos'))

    def test_vencimientos_view_rejects_invalid_range(self):
        response = self.client.post(reverse('matafuegos:vencimientos'), {
            'inicio': '2024-06-01', 'fin': '2024-01-01',
        })
        self.assertRedirects(response, reverse('matafuegos:vencimientos'))

    def test_proximos_vencimientos_without_data_redirects_with_error(self):
        response = self.client.get(reverse('matafuegos:proximos-vencimientos'))
        self.assertRedirects(response, reverse('matafuegos:list'))


class MisMatafuegosViewsTests(TestCase):
    def test_cliente_final_sees_only_own_matafuegos(self):
        cliente = ClienteFactory()
        user = User.objects.create_user(
            username='cliente_final', password='testpass123',
            company=cliente.company, role=Role.CLIENTE_FINAL, cliente=cliente,
        )
        matafuego = MatafuegosFactory(cliente=cliente)
        MatafuegosFactory()

        self.client.force_login(user)
        response = self.client.get(reverse('matafuegos:mis-matafuegos'))

        self.assertEqual(list(response.context['matafuegos']), [matafuego])
