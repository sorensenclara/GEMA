from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from accounts.models import Role
from core.services import GeocodingError
from empresas.tests.factories import CompanyFactory

User = get_user_model()


class ClienteUbicacionBuscarViewTests(TestCase):
    def setUp(self):
        self.company = CompanyFactory()
        self.user = User.objects.create_user(
            username='operador', password='testpass123',
            company=self.company, role=Role.OPERADOR,
        )
        self.client.force_login(self.user)

    def test_requiere_login(self):
        self.client.logout()
        response = self.client.get(reverse('cliente:ubicacion-buscar'), {'q': 'San Cayetano'})
        self.assertNotEqual(response.status_code, 200)

    @patch('cliente.views.geocoding.buscar_ubicaciones')
    def test_devuelve_los_resultados_del_servicio_de_geocodificacion(self, mock_buscar):
        mock_buscar.return_value = [{'token': 'abc', 'direccion': 'Av. San Martín 450, San Cayetano'}]

        response = self.client.get(reverse('cliente:ubicacion-buscar'), {'q': 'San Martin 450'})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'resultados': [{'token': 'abc', 'direccion': 'Av. San Martín 450, San Cayetano'}]})
        mock_buscar.assert_called_once_with('San Martin 450')

    @patch('cliente.views.geocoding.buscar_ubicaciones')
    def test_si_falla_el_proveedor_devuelve_vacio_en_vez_de_romper(self, mock_buscar):
        mock_buscar.side_effect = GeocodingError('nominatim no respondió')

        response = self.client.get(reverse('cliente:ubicacion-buscar'), {'q': 'lo que sea'})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'resultados': []})
