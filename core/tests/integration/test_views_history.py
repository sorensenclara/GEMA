from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from accounts.models import Role
from cliente.tests.factories import ClienteFactory

User = get_user_model()


class HistoryViewTests(TestCase):
    def test_shows_history_for_audited_model(self):
        cliente = ClienteFactory(nombre='Nombre original')
        cliente.nombre = 'Nombre actualizado'
        cliente.save()

        user = User.objects.create_user(
            username='admin_empresa', password='testpass123',
            company=cliente.company, role=Role.ADMIN_EMPRESA,
        )
        self.client.force_login(user)

        response = self.client.get(reverse('core:history', args=['cliente', 'cliente', cliente.pk]))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['page_obj'].object_list), 2)

    def test_404_for_model_without_history(self):
        user = User.objects.create_user(username='u', password='testpass123', is_superuser=True)
        self.client.force_login(user)

        response = self.client.get(reverse('core:history', args=['auth', 'permission', 1]))

        self.assertEqual(response.status_code, 404)
