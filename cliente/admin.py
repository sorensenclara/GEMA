import smtplib
from datetime import date, timedelta
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from django.contrib import admin, messages
from django.http import FileResponse, HttpResponse
from io import BytesIO

from .forms import ControlWebForm
from .models import Cliente
from orden_trabajo.models import Ordenes_de_trabajo,TareaOrden
from matafuegos.models import Matafuegos

#ACCIONES
from django.conf import settings

from empresas.admin_mixins import CompanyScopedAdmin
from reports.branding import report_header_context
from reports.pdf_render import render_report_pdf


@admin.action(description='Estado inactivo')
def make_inactivo(modeladmin, request, queryset):
    queryset.update(estado='i')

@admin.action(description='Estado activo')
def make_activo(modeladmin, request, queryset):
    queryset.update(estado='a')

def generarInformeCliente(request, queryset):
    set = queryset.all()
    if set.count() > 1:
        messages.error(request, 'Debe seleccionar solo un cliente')
        return None
    d = set.first()
    context = report_header_context(d, 'Informe del cliente')
    context.update({
        'cliente': d,
        'matafuegos': Matafuegos.objects.filter(cliente=d).order_by('numeroInterno'),
    })
    return render_report_pdf('reports/informe_cliente.html', context)

def generarListadoClientes(queryset):
    clientes = list(queryset)
    context = report_header_context(clientes[0] if clientes else None, 'Listado de clientes')
    context['clientes'] = clientes
    return render_report_pdf('reports/listado_clientes.html', context)

@admin.action(description="Enviar informe al cliente")
def send_email(self, request, queryset):
        set = queryset.all()
        if set.count()>1:
            return messages.error(request,'Debe seleccionar solo un cliente')
        else:
            for d in set:
                if d.email:
                     mail_to = d.email
                     nombre= str(d.nombre)
                     company = d.company
                else:
                     return messages.error(request,'El cliente seleccionado no tiene un email especificado')
        pdf_bytes = generarInformeCliente(request, queryset)
        if pdf_bytes is None:
            return
        buffer = BytesIO(pdf_bytes)
        mailServer = smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT)
        mailServer.ehlo()
        mailServer.starttls()
        mailServer.ehlo()
        email = company.smtp_email
        contraseña = company.smtp_password
        if not (email and contraseña):
            return messages.error(request,'No hay un email especificado')
        try:
            mailServer.login(email, contraseña)
        except:
            return messages.error(request,'El email o la contraseña de la empresa no es correcta')
        mensaje = MIMEMultipart()
        attach = MIMEApplication(pdf_bytes, _subtype="pdf")
        attach.add_header('Content-Disposition','attachment',filename=str('informeCliente.pdf'))
        mensaje.attach(MIMEText('Hola '+ nombre + ', te compartimos el informe con la información de tus matafuegos y las ordenes de trabajo. \n ', 'plain'))
        mensaje.attach(MIMEText('Muchas gracias! ', 'plain'))
        mensaje.attach(attach)
        mensaje['From'] = email #settings.EMAIL_HOST_USER
        mensaje['To']= mail_to
        mensaje['Subject'] = "Informe " + company.nombre
        mailServer.sendmail(email, mail_to, mensaje.as_string())
        messages.success(request, "Email enviado correctamente")
        buffer.seek(0)
        messages.success(request, "Informe emitido")
        return FileResponse(buffer, as_attachment=True, filename='Informe cliente.pdf')



#Emite el informe con la informacion de un cliente, los matafuegos que tiene asociado y las tareas.
@admin.action(description="Informe del cliente")
def emitirInformeCliente(self, request, queryset):
        pdf_bytes = generarInformeCliente(request, queryset)
        if pdf_bytes is None:
            return
        messages.success(request, "Informe emitido")
        return FileResponse(BytesIO(pdf_bytes), as_attachment=True, filename='Informe cliente.pdf')


class OrdenTrabajoTabularInline(admin.TabularInline):
    model = Ordenes_de_trabajo
    can_delete = False
    fields = ('fecha_creacion','fecha_inicio','fecha_entrega','fecha_cierre','cliente','estado','monto_total',)
    def has_change_permission(self, request, obj=None):
        return False
    def has_add_permission(self, request, obj=None):
        return False

class MatafuegoTabularInline(admin.TabularInline):
    model = Matafuegos
    can_delete = False
    fields = ('numero', 'numero_dps', 'direccion', 'categoria', 'tipo', 'fecha_fabricacion', 'vencido')
    ordering = ('numero_dps',)
    def has_change_permission(self, request, obj=None):
        return False
    def has_add_permission(self, request, obj=None):
        return False
class CLienteAdmin(CompanyScopedAdmin, admin.ModelAdmin):

    list_display = (
        'codigo',
        'cuit_cuil',
        'nombre',
        'direccion',
    )

    search_fields= ('codigo', 'nombre', 'cuit_cuil','contacto',)
    list_filter= ('estado', 'tipo',)
    actions = [make_inactivo, make_activo, emitirInformeCliente, send_email]
    inlines = [OrdenTrabajoTabularInline, MatafuegoTabularInline]
    ordering = ['nombre']
    list_per_page = 50
    list_max_show_all = 500 # Here
    #form = ControlWebForm

admin.site.register(Cliente, CLienteAdmin)
