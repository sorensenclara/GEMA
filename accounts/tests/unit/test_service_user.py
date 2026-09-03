from django.test import TestCase

from accounts.exceptions import NoPuedeDesactivarsePropioUsuarioException
from accounts.services import activar_usuario, desactivar_usuario, invitar_usuario
from accounts.tests.factories import UserFactory


class DesactivarUsuarioTests(TestCase):
    def test_deactivates_a_different_user(self):
        acting_user = UserFactory()
        target = UserFactory()

        desactivar_usuario(target, acting_user)

        target.refresh_from_db()
        self.assertFalse(target.is_active)

    def test_raises_when_target_is_acting_user(self):
        user = UserFactory()

        with self.assertRaises(NoPuedeDesactivarsePropioUsuarioException):
            desactivar_usuario(user, user)


class ActivarUsuarioTests(TestCase):
    def test_activates_user(self):
        user = UserFactory(is_active=False)

        activar_usuario(user)

        user.refresh_from_db()
        self.assertTrue(user.is_active)


class InvitarUsuarioTests(TestCase):
    def test_sends_email_when_user_has_email(self):
        from django.core import mail

        user = UserFactory(email='nuevo@example.com')

        enviada = invitar_usuario(user, domain='gema.example.com', use_https=True)

        self.assertTrue(enviada)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('nuevo@example.com', mail.outbox[0].to)

    def test_returns_false_without_email(self):
        user = UserFactory(email='')

        enviada = invitar_usuario(user, domain='gema.example.com', use_https=True)

        self.assertFalse(enviada)
