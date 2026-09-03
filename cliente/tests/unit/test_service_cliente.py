from unittest.mock import MagicMock, patch

from django.test import TestCase

from cliente.exceptions import (
    ClienteSinEmailException,
    CredencialesSmtpInvalidasException,
    SmtpNoConfiguradoException,
)
from cliente.services import enviar_informe_por_email, generar_informe_cliente, generar_listado_clientes
from cliente.tests.factories import ClienteFactory
from empresas.tests.factories import CompanyFactory


class GenerarInformeClienteTests(TestCase):
    def test_returns_valid_pdf_bytes(self):
        cliente = ClienteFactory()
        pdf_bytes = generar_informe_cliente(cliente)
        self.assertTrue(pdf_bytes.startswith(b'%PDF'))


class GenerarListadoClientesTests(TestCase):
    def test_returns_valid_pdf_bytes_for_empty_queryset(self):
        pdf_bytes = generar_listado_clientes([])
        self.assertTrue(pdf_bytes.startswith(b'%PDF'))

    def test_returns_valid_pdf_bytes_with_clientes(self):
        from cliente.models import Cliente

        ClienteFactory.create_batch(2)
        pdf_bytes = generar_listado_clientes(Cliente.objects.all())
        self.assertTrue(pdf_bytes.startswith(b'%PDF'))


class EnviarInformePorEmailTests(TestCase):
    def test_raises_when_cliente_has_no_email(self):
        cliente = ClienteFactory(email='')
        with self.assertRaises(ClienteSinEmailException):
            enviar_informe_por_email(cliente)

    def test_raises_when_company_has_no_smtp_configured(self):
        company = CompanyFactory(smtp_email='', smtp_password='')
        cliente = ClienteFactory(company=company, email='cliente@example.com')
        with self.assertRaises(SmtpNoConfiguradoException):
            enviar_informe_por_email(cliente)

    @patch('cliente.services.cliente.smtplib.SMTP')
    def test_raises_credenciales_invalidas_on_login_failure(self, mock_smtp_class):
        import smtplib

        mock_server = MagicMock()
        mock_server.login.side_effect = smtplib.SMTPAuthenticationError(535, b'bad credentials')
        mock_smtp_class.return_value = mock_server

        company = CompanyFactory(smtp_email='empresa@example.com', smtp_password='wrong')
        cliente = ClienteFactory(company=company, email='cliente@example.com')

        with self.assertRaises(CredencialesSmtpInvalidasException):
            enviar_informe_por_email(cliente)

    @patch('cliente.services.cliente.smtplib.SMTP')
    def test_sends_email_and_returns_pdf_bytes(self, mock_smtp_class):
        mock_server = MagicMock()
        mock_smtp_class.return_value = mock_server

        company = CompanyFactory(smtp_email='empresa@example.com', smtp_password='secreto')
        cliente = ClienteFactory(company=company, email='cliente@example.com')

        pdf_bytes = enviar_informe_por_email(cliente)

        self.assertTrue(pdf_bytes.startswith(b'%PDF'))
        mock_server.login.assert_called_once_with('empresa@example.com', 'secreto')
        mock_server.sendmail.assert_called_once()
