import smtplib
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from django.conf import settings

from cliente.exceptions import (
    ClienteSinEmailException,
    CredencialesSmtpInvalidasException,
    SmtpNoConfiguradoException,
)
from matafuegos.models import Matafuegos
from reports.services import render_report_pdf, report_header_context


def generar_informe_cliente(cliente):
    """Informe de un cliente con sus matafuegos asociados."""
    context = report_header_context(cliente, 'Informe del cliente')
    context.update({
        'cliente': cliente,
        'matafuegos': Matafuegos.objects.filter(cliente=cliente).order_by('numeroInterno'),
    })
    return render_report_pdf('reports/informe_cliente.html', context)


def generar_listado_clientes(clientes):
    clientes = list(clientes)
    context = report_header_context(clientes[0] if clientes else None, 'Listado de clientes')
    context['clientes'] = clientes
    return render_report_pdf('reports/listado_clientes.html', context)


def enviar_informe_por_email(cliente):
    """Genera el informe del cliente y lo envía por email usando el SMTP
    propio de la compañía (Company.smtp_email/smtp_password) contra el
    servidor configurado en settings.EMAIL_HOST/EMAIL_PORT. Devuelve los
    bytes del PDF enviado, para que la vista pueda además ofrecerlo como
    descarga (comportamiento ya existente)."""
    if not cliente.email:
        raise ClienteSinEmailException('El cliente seleccionado no tiene un email especificado.')

    company = cliente.company
    email = company.smtp_email
    password = company.smtp_password
    if not (email and password):
        raise SmtpNoConfiguradoException('La compañía no tiene un email SMTP configurado.')

    pdf_bytes = generar_informe_cliente(cliente)

    mail_server = smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT)
    mail_server.ehlo()
    mail_server.starttls()
    mail_server.ehlo()
    try:
        mail_server.login(email, password)
    except smtplib.SMTPException as exc:
        raise CredencialesSmtpInvalidasException('El email o la contraseña de la empresa no es correcta.') from exc

    mensaje = MIMEMultipart()
    attach = MIMEApplication(pdf_bytes, _subtype='pdf')
    attach.add_header('Content-Disposition', 'attachment', filename='informeCliente.pdf')
    mensaje.attach(MIMEText(
        f'Hola {cliente.nombre}, te compartimos el informe con la información de tus '
        'matafuegos y las ordenes de trabajo. \n ', 'plain',
    ))
    mensaje.attach(MIMEText('Muchas gracias! ', 'plain'))
    mensaje.attach(attach)
    mensaje['From'] = email
    mensaje['To'] = cliente.email
    mensaje['Subject'] = f'Informe {company.nombre}'
    mail_server.sendmail(email, cliente.email, mensaje.as_string())
    return pdf_bytes
