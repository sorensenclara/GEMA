from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from accounts.models import Role
from cliente.tests.factories import ClienteFactory
from empresas.tests.factories import CompanyFactory
from matafuegos.tests.factories import MatafuegosFactory
from orden_trabajo.models import Ordenes_de_trabajo, TareaOrden
from orden_trabajo.tests.factories import OrdenesDeTrabajoFactory, TareaFactory

User = get_user_model()


class OrdenViewsTests(TestCase):
    def setUp(self):
        self.company = CompanyFactory()
        self.user = User.objects.create_user(
            username='operador', password='testpass123',
            company=self.company, role=Role.OPERADOR,
        )
        self.client.force_login(self.user)

    def test_list_shows_only_company_ordenes(self):
        OrdenesDeTrabajoFactory(matafuegos__cliente__company=self.company)
        OrdenesDeTrabajoFactory()

        response = self.client.get(reverse('orden_trabajo:orden-list'))

        self.assertEqual(len(response.context['ordenes']), 1)

    def test_create_orden_with_tarea_recalculates_monto(self):
        cliente = ClienteFactory(company=self.company)
        matafuego = MatafuegosFactory(cliente=cliente)
        tarea = TareaFactory(company=self.company, precio=250)

        response = self.client.post(reverse('orden_trabajo:orden-create'), {
            'cliente': cliente.pk, 'matafuegos': matafuego.pk,
            'fecha_inicio': '2024-01-01', 'fecha_entrega': '2024-01-05', 'fecha_cierre': '',
            'estado': 'ep', 'notas': '',
            'tareaorden_set-TOTAL_FORMS': '1', 'tareaorden_set-INITIAL_FORMS': '0',
            'tareaorden_set-MIN_NUM_FORMS': '0', 'tareaorden_set-MAX_NUM_FORMS': '1000',
            'tareaorden_set-0-tarea': tarea.pk, 'tareaorden_set-0-cant_cargada': '1', 'tareaorden_set-0-precioAj': '0',
        })

        self.assertEqual(response.status_code, 302)
        orden = Ordenes_de_trabajo.objects.get(cliente=cliente)
        self.assertEqual(orden.monto_total, 250)
        self.assertEqual(TareaOrden.objects.filter(orden=orden).count(), 1)


class OrdenCambiarEstadoViewTests(TestCase):
    def setUp(self):
        self.company = CompanyFactory()
        self.user = User.objects.create_user(
            username='operador', password='testpass123',
            company=self.company, role=Role.OPERADOR,
        )
        self.client.force_login(self.user)

    def test_iniciar_avanza_de_pendiente_a_en_proceso(self):
        orden = OrdenesDeTrabajoFactory(matafuegos__cliente__company=self.company, estado='p')

        response = self.client.post(reverse('orden_trabajo:orden-cambiar-estado', args=[orden.pk, 'iniciar']))

        self.assertRedirects(response, reverse('orden_trabajo:orden-list'))
        orden.refresh_from_db()
        self.assertEqual(orden.estado, 'ep')

    def test_transicion_invalida_muestra_error_y_no_cambia_estado(self):
        orden = OrdenesDeTrabajoFactory(matafuegos__cliente__company=self.company, estado='p')

        response = self.client.post(reverse('orden_trabajo:orden-cambiar-estado', args=[orden.pk, 'facturar']))

        self.assertRedirects(response, reverse('orden_trabajo:orden-list'))
        orden.refresh_from_db()
        self.assertEqual(orden.estado, 'p')

    def test_no_puede_cambiar_estado_de_orden_de_otra_compania(self):
        orden = OrdenesDeTrabajoFactory(estado='p')

        response = self.client.post(reverse('orden_trabajo:orden-cambiar-estado', args=[orden.pk, 'iniciar']))

        self.assertEqual(response.status_code, 404)


class TareaViewsTests(TestCase):
    def setUp(self):
        self.company = CompanyFactory()
        self.user = User.objects.create_user(
            username='operador', password='testpass123',
            company=self.company, role=Role.OPERADOR,
        )
        self.client.force_login(self.user)

    def test_create_tarea(self):
        response = self.client.post(reverse('orden_trabajo:tarea-create'), {
            'nombre': 'Recarga', 'precio': '150', 'es_recarga': 'on',
        })
        self.assertEqual(response.status_code, 302)
