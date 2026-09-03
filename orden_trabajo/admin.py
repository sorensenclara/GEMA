from datetime import date
from io import BytesIO

from django.contrib import admin, messages
from django.contrib.admin.helpers import ACTION_CHECKBOX_NAME
from django.http import FileResponse
from django.utils.translation import gettext_lazy as _

from core.exceptions import DomainException
from empresas.admin_mixins import CompanyScopedAdmin
from orden_trabajo.exceptions import DebeSeleccionarUnaOrdenException
from orden_trabajo.forms import OrdenesTrabajoAdminForm
from orden_trabajo.models import Ordenes_de_trabajo, Tarea, TareaOrden
from orden_trabajo.selectors import list_ordenes_ultima_semana
from orden_trabajo.services import (
    emitir_informe_facturacion,
    emitir_informe_facturacion_ultima_semana,
    emitir_informe_orden,
    emitir_oblea_domiciliaria,
    emitir_oblea_vehicular,
    recalcular_monto_total,
)


class TareaAdmin(CompanyScopedAdmin, admin.ModelAdmin):
    list_display = (
        'nombre',
        'precio',
        'es_recarga',
    )


class TareaScopedInlineMixin:
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'tarea' and not request.user.is_superuser:
            kwargs['queryset'] = Tarea.objects.filter(company=request.user.company)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


class TareaTabularInline(TareaScopedInlineMixin, admin.TabularInline):
    model = TareaOrden
    can_delete = True
    fields = ('tarea', 'cant_cargada')


class TareaFinalizadaTabularInline(TareaScopedInlineMixin, admin.TabularInline):
    model = TareaOrden
    can_delete = True
    fields = ('tarea', 'cant_cargada')

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False


# ACCIONES

@admin.action(description='Finalizar orden de trabajo')
def action_finalizada(modeladmin, request, queryset):
    queryset.update(fecha_cierre=date.today())
    queryset.update(estado='f')


@admin.action(description='Cancelar orden de trabajo')
def action_cancelada(modeladmin, request, queryset):
    queryset.update(estado='c')


@admin.action(description='Orden facturada')
def action_facturada(modeladmin, request, queryset):
    queryset.update(estado='fac')


def _pdf_o_error(request, func, *args, filename):
    try:
        pdf_bytes = func(*args)
    except DomainException as exc:
        messages.error(request, str(exc))
        return None
    messages.success(request, "Informe emitido")
    return FileResponse(BytesIO(pdf_bytes), as_attachment=True, filename=filename)


@admin.action(description="Oblea DPS vehicular")
def emitirInformeVehicular(modeladmin, request, queryset):
    return _pdf_o_error(request, emitir_oblea_vehicular, queryset, filename='oblea_DPS_vehicular.pdf')


@admin.action(description="Oblea DPS Domiciliaria")
def emitirInformeDPSFijo(modeladmin, request, queryset):
    return _pdf_o_error(request, emitir_oblea_domiciliaria, queryset, filename='oblea_DPS_domiciliaria.pdf')


def _una_sola_orden(queryset):
    if queryset.count() != 1:
        raise DebeSeleccionarUnaOrdenException('Seleccionar una orden.')
    return queryset.first()


@admin.action(description="Informe Ordenes de trabajo")
def emitirInformeOrden(modeladmin, request, queryset):
    try:
        orden = _una_sola_orden(queryset)
    except DomainException as exc:
        messages.error(request, str(exc))
        return
    return _pdf_o_error(request, emitir_informe_orden, orden, filename='informe de orden.pdf')


@admin.action(description="Informe Facturación")
def InformeFacturacion(modeladmin, request, queryset):
    return _pdf_o_error(request, emitir_informe_facturacion, queryset, filename='informe_facturacion.pdf')


class DecadeBornListFilter(admin.SimpleListFilter):
    title = _('categoria')
    parameter_name = 'matafuegos__categoria'

    def lookups(self, request, model_admin):
        return (
            ('d', _('Domiciliaria')),
            ('v', _('Vehicular')),
        )

    def queryset(self, request, queryset):
        if self.value() == 'v':
            return queryset.filter(matafuegos__categoria='v') | queryset.filter(matafuegos__categoria='ma')
        if self.value() == 'd':
            return queryset.filter(matafuegos__categoria='d')


class FilterEstado(admin.SimpleListFilter):
    title = _('estado multiple')
    parameter_name = 'estado'

    def lookups(self, request, model_admin):
        return (
            ('p', _('Pendiente')),
            ('ep', _('En proceso')),
            ('i', _('Impresa')),
            ('fac', _('Facturada')),
            ('f', _('Finalizada')),
            ('c', _('Cancelada')),
            ('fi', _('Finalizada-Impresa')),
        )

    def queryset(self, request, queryset):
        if self.value() == 'fi':
            return queryset.filter(estado='f') | queryset.filter(estado='i')
        if self.value() in ('p', 'ep', 'i', 'fac', 'f', 'c'):
            return queryset.filter(estado=self.value())


class OrdenTrabajoAdmin(CompanyScopedAdmin, admin.ModelAdmin):
    list_display = (
        'id',
        'cliente',
        'matafuegos',
        'get_categoria',
        'estado',
        'fecha_creacion',
    )

    def get_categoria(self, obj):
        if obj.matafuegos.categoria == 'd':
            return 'Domiciliaria'
        return 'Vehicular'
    get_categoria.short_description = 'Categoria'
    autocomplete_fields = ('cliente',)
    search_fields = ('id', 'cliente__codigo', 'cliente__nombre', 'fecha_creacion', 'matafuegos__numero')
    list_filter = (DecadeBornListFilter, FilterEstado)
    inlines = [TareaTabularInline]
    model = Ordenes_de_trabajo
    actions = [action_finalizada, action_facturada, emitirInformeDPSFijo, emitirInformeVehicular, InformeFacturacion, emitirInformeOrden, 'Informe_facturacion_ultimaSemana']
    ordering = ['-fecha_cierre']
    form = OrdenesTrabajoAdminForm
    list_per_page = 15
    list_max_show_all = 500

    def save_model(self, request, obj, form, change):
        obj.usuario = request.user.username
        super().save_model(request, obj, form, change)

    def save_formset(self, request, form, formset, change):
        formset.save()
        if formset.model is TareaOrden:
            recalcular_monto_total(form.instance)

    def get_readonly_fields(self, request, obj=None):
        if obj is not None and obj.estado in ('f', 'c', 'i'):
            OrdenTrabajoAdmin.inlines = [TareaFinalizadaTabularInline]
            return ['id', 'fecha_inicio', 'fecha_entrega', 'fecha_creacion', 'notas', 'estado', 'monto_total', 'matafuegos', 'cliente', 'usuario']
        OrdenTrabajoAdmin.inlines = [TareaTabularInline]
        return ['fecha_inicio', 'fecha_cierre', 'monto_total', 'estado', 'usuario']

    """Funcion para que no sea necesario seleccionar una para el informe de facturacion"""
    def changelist_view(self, request, extra_context=None):
        if 'action' in request.POST and (request.POST['action'] == 'Informe_facturacion_uiltimaSemana'):
            if not request.POST.getlist(ACTION_CHECKBOX_NAME):
                primero = self.get_queryset(request).first()
                if primero is not None:
                    post = request.POST.copy()
                    post.update({ACTION_CHECKBOX_NAME: str(primero.id)})
                    request._set_post(post)
        return super().changelist_view(request, extra_context)

    @admin.action(description="Informe Facturación ultima semana")
    def Informe_facturacion_ultimaSemana(self, request, obj):
        ordenes = list_ordenes_ultima_semana(request.user.company)
        return _pdf_o_error(request, emitir_informe_facturacion_ultima_semana, ordenes, filename='informe_facturacion.pdf')


class TareaOrdenAdmin(admin.ModelAdmin):
    list_display = (
        'tarea',
        'orden',
    )

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(orden__company=request.user.company)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if not request.user.is_superuser:
            if db_field.name == 'tarea':
                kwargs['queryset'] = Tarea.objects.filter(company=request.user.company)
            elif db_field.name == 'orden':
                kwargs['queryset'] = Ordenes_de_trabajo.objects.filter(company=request.user.company)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        recalcular_monto_total(obj.orden)


admin.site.register(Ordenes_de_trabajo, OrdenTrabajoAdmin)
admin.site.register(Tarea, TareaAdmin)
admin.site.register(TareaOrden, TareaOrdenAdmin)
