from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from accounts.models import Role
from cliente.models import Cliente
from cliente.tests.factories import ClienteFactory
from django.core.cache import cache

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

    def test_create_cliente_sin_usar_el_buscador_de_ubicacion_queda_manual(self):
        """Sin tocar el buscador (JS deshabilitado, o directamente no se usó):
        la creación del cliente nunca debe quedar bloqueada por esto."""
        response = self.client.post(reverse('cliente:create'), {
            'codigo': '2', 'nombre': 'Cliente sin buscador', 'direccion': 'Una direccion cualquiera 123',
            'telefono': '2233445566', 'tipo': 'p', 'estado': 'a',
        })

        self.assertEqual(response.status_code, 302)
        cliente = Cliente.objects.get(codigo='2')
        self.assertEqual(cliente.direccion, 'Una direccion cualquiera 123')
        self.assertEqual(cliente.geo_status, 'manual_no_encontrado')
        self.assertIsNone(cliente.localidad or None)

    def test_create_cliente_con_seleccion_valida_guarda_datos_estructurados(self):
        token = 'token-de-prueba-123'
        cache.set(f'geocoding:seleccion:{token}', {
            'direccion': 'Av. San Martín 450, San Cayetano, Buenos Aires, Argentina',
            'localidad': 'San Cayetano',
            'provincia': 'Buenos Aires',
            'codigo_postal': '7609',
            'pais': 'Argentina',
            'geo_referencia_externa': 'way:123456789',
        }, timeout=60)

        response = self.client.post(reverse('cliente:create'), {
            'codigo': '3', 'nombre': 'Cliente georreferenciado',
            # El texto tipeado por el usuario no importa una vez que hay una
            # seleccion valida: el servidor guarda la direccion normalizada
            # que vino de la busqueda, no lo que haya en el input.
            'direccion': 'texto que el usuario habia escrito antes de buscar',
            'telefono': '2233445566', 'tipo': 'p', 'estado': 'a',
            'geo_tocado': '1', 'geo_seleccion_token': token,
        })

        self.assertEqual(response.status_code, 302)
        cliente = Cliente.objects.get(codigo='3')
        self.assertEqual(cliente.direccion, 'Av. San Martín 450, San Cayetano, Buenos Aires, Argentina')
        self.assertEqual(cliente.localidad, 'San Cayetano')
        self.assertEqual(cliente.provincia, 'Buenos Aires')
        self.assertEqual(cliente.codigo_postal, '7609')
        self.assertEqual(cliente.pais, 'Argentina')
        self.assertEqual(cliente.geo_referencia_externa, 'way:123456789')
        self.assertEqual(cliente.geo_provider, 'nominatim')
        self.assertEqual(cliente.geo_status, 'georreferenciado')

    def test_create_cliente_con_token_vencido_queda_manual_no_encontrado(self):
        response = self.client.post(reverse('cliente:create'), {
            'codigo': '4', 'nombre': 'Cliente rural',
            'direccion': 'Zona rural sin nomenclatura, Partido de San Cayetano',
            'telefono': '2233445566', 'tipo': 'p', 'estado': 'a',
            'geo_tocado': '1', 'geo_seleccion_token': 'token-que-no-existe',
        })

        self.assertEqual(response.status_code, 302)
        cliente = Cliente.objects.get(codigo='4')
        self.assertEqual(cliente.direccion, 'Zona rural sin nomenclatura, Partido de San Cayetano')
        self.assertEqual(cliente.geo_status, 'manual_no_encontrado')
        self.assertEqual(cliente.localidad, '')
        self.assertEqual(cliente.geo_referencia_externa, '')

    def test_editar_cliente_sin_tocar_ubicacion_no_pierde_datos_georreferenciados(self):
        cliente = ClienteFactory(
            company=self.company, direccion='Av. San Martín 450, San Cayetano, Buenos Aires, Argentina',
            localidad='San Cayetano', provincia='Buenos Aires', codigo_postal='7609', pais='Argentina',
            geo_referencia_externa='way:123456789', geo_provider='nominatim', geo_status='georreferenciado',
        )

        response = self.client.post(reverse('cliente:update', args=[cliente.pk]), {
            'codigo': cliente.codigo, 'nombre': cliente.nombre,
            'direccion': cliente.direccion, 'telefono': '2233445566', 'tipo': 'p', 'estado': 'a',
            # geo_tocado ausente: el usuario no interactuo con el buscador.
        })

        self.assertEqual(response.status_code, 302)
        cliente.refresh_from_db()
        self.assertEqual(cliente.localidad, 'San Cayetano')
        self.assertEqual(cliente.geo_status, 'georreferenciado')

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
