from io import BytesIO

from django.contrib import admin, messages
from django.http import FileResponse

from cliente.exceptions import DebeSeleccionarUnSoloClienteException
from cliente.models import Cliente
from cliente.services import enviar_informe_por_email, generar_informe_cliente
from core.exceptions import DomainException
from empresas.admin_mixins import CompanyScopedAdmin
from matafuegos.models import Matafuegos
from orden_trabajo.models import Ordenes_de_trabajo


@admin.action(description='Estado inactivo')
def make_inactivo(modeladmin, request, queryset):
    queryset.update(estado='i')


@admin.action(description='Estado activo')
def make_activo(modeladmin, request, queryset):
    queryset.update(estado='a')


def _un_solo_cliente(queryset):
    if queryset.count() != 1:
        raise DebeSeleccionarUnSoloClienteException('Debe seleccionar solo un cliente.')
    return queryset.first()


@admin.action(description="Informe del cliente")
def emitirInformeCliente(modeladmin, request, queryset):
    try:
        cliente = _un_solo_cliente(queryset)
        pdf_bytes = generar_informe_cliente(cliente)
    except DomainException as exc:
        messages.error(request, str(exc))
        return
    messages.success(request, "Informe emitido")
    return FileResponse(BytesIO(pdf_bytes), as_attachment=True, filename='Informe cliente.pdf')


@admin.action(description="Enviar informe al cliente")
def send_email(modeladmin, request, queryset):
    try:
        cliente = _un_solo_cliente(queryset)
        pdf_bytes = enviar_informe_por_email(cliente)
    except DomainException as exc:
        messages.error(request, str(exc))
        return
    messages.success(request, "Email enviado correctamente")
    messages.success(request, "Informe emitido")
    return FileResponse(BytesIO(pdf_bytes), as_attachment=True, filename='Informe cliente.pdf')


class OrdenTrabajoTabularInline(admin.TabularInline):
    model = Ordenes_de_trabajo
    can_delete = False
    fields = ('fecha_creacion', 'fecha_inicio', 'fecha_entrega', 'fecha_cierre', 'cliente', 'estado', 'monto_total')

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
        'geo_status',
    )

    # Datos geográficos: no editables desde el admin, se resuelven solo
    # desde el buscador de ubicaciones del formulario de Cliente (ver
    # cliente/forms/cliente.py); acá quedan visibles solo para soporte.
    readonly_fields = ('localidad', 'provincia', 'codigo_postal', 'pais', 'geo_referencia_externa', 'geo_provider', 'geo_status')

    search_fields = ('codigo', 'nombre', 'cuit_cuil', 'contacto')
    list_filter = ('estado', 'tipo', 'geo_status')
    actions = [make_inactivo, make_activo, emitirInformeCliente, send_email]
    inlines = [OrdenTrabajoTabularInline, MatafuegoTabularInline]
    ordering = ['nombre']
    list_per_page = 50
    list_max_show_all = 500


admin.site.register(Cliente, CLienteAdmin)
