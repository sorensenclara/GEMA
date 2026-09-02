from datetime import date, timedelta
from io import BytesIO
from itertools import chain, groupby
from urllib import request

from django.contrib.admin.helpers import ACTION_CHECKBOX_NAME
from django.db.models import Q
from django.http import FileResponse
from reportlab.pdfgen import canvas
from django.contrib import admin, messages
from reportlab.lib.units import inch
from .forms import OrdenesTrabajoAdminForm
from .models import Tarea, Ordenes_de_trabajo, TareaOrden, Matafuegos
from empresas.admin_mixins import CompanyScopedAdmin
from reports.branding import resolve_company_name, report_header_context
from reports.pdf_render import render_report_pdf
from datetime import date

from django.contrib import admin
from django.utils.translation import gettext_lazy as _


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
    fields = ('tarea','cant_cargada')
    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

#ACCIONES

#Accion para iniciar la orden y pasar de estado pendiente a en proceso. -No usada por ahora porque ya inicia en 'En proceso'
@admin.action(description='Iniciar orden de trabajo')
def action_iniciada(modeladmin, request, queryset):
    queryset.update(estado='ep')
    queryset.update(fecha_inicio=date.today())
    queryset.update(fecha_cierre=None)

# Accion para finalizar la orden y pasar a estado finalizada
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

@admin.action(description="Oblea DPS vehicular")
def emitirInformeVehicular(self, request, queryset):
    # Create file to recieve data and create the PDF
    buffer = BytesIO()
    # Create the file PDF
    pdf = canvas.Canvas(buffer)
    pdf.setPageSize((6.69291*inch, 12*inch))
    # Inserting in PDF where this 2 first arguments are axis X and Y respectvely
    set = queryset.all()
    y = 780  # 775 queda bajo 787 queda alto
    x = 23
    pdf.setFont("Helvetica", 10)
    cant = set.count()
    if set.count() % 2 != 0:
        return messages.error(request,'La cantidad de ordenes de trabajo debe ser multiple de dos')
    else:
        for d in set:
            if d.matafuegos.categoria != 'v' and d.matafuegos.categoria != 'ma':
                return messages.error(request,'Seleccionar solo categoria vehicular')
        for d in set:
            if d.estado != 'f' and d.estado != 'i':
                return messages.error(request,'Orden no finalizada')
        for d in set:
            if not d.fecha_cierre:
                return messages.error(request, f'La orden N° {d.id} no tiene fecha de cierre: no se puede emitir la oblea.')
        for d in set:
            if not TareaOrden.objects.filter(orden=d, tarea__es_recarga=True).exists():
                return messages.error(request, f'La orden N° {d.id} no tiene ninguna tarea de recarga: no se puede emitir la oblea.')
        for d in set:
            d.estado='i'
            d.save()
            for orden in TareaOrden.objects.filter(orden=d):
                    if orden.tarea.es_recarga:
                        d.matafuegos.fecha_carga = d.fecha_cierre
                    if orden.tarea.nombre == 'Prueba Hidráulica':
                        d.matafuegos.fecha_ph= d.fecha_cierre
            d.matafuegos.numero_dps = d.company.incrementar_dps('veh')
            d.matafuegos.save()
            pdf.drawString(x+3, y, str(d.matafuegos.numero))
            pdf.drawString(x+71, y,str(d.matafuegos.fecha_fabricacion.year))
            try:
                pdf.drawString(x+110, y,str(d.matafuegos.fecha_proxima_ph.month)+" "+str(d.matafuegos.fecha_proxima_ph.year))
            except:
                pass
            pdf.drawString(x+145, y,str(d.matafuegos.tipo.volumen))
            pdf.drawString(x+176, y,str(d.matafuegos.tipo))
            pdf.drawString(x+3, y-23, resolve_company_name(d))
            pdf.drawString(x+128, y-23, str("120"))
            pdf.drawString(x+270, y-22, str(d.matafuegos.numero)) #254 #23
            try:
                pdf.drawString(x+316, y-22, str(d.matafuegos.fecha_proxima_ph.month)+" "+str(d.matafuegos.fecha_proxima_ph.year)) # 308 #23
            except:
                pass
            try:
                pdf.drawString(x+8, y-60, str(d.matafuegos.fecha_proxima_carga.month))
                pdf.drawString(x+35, y-60, str(d.matafuegos.fecha_proxima_carga.year))
            except:
                pass
            pdf.drawString(x+163, y-60, str(d.matafuegos.patente))
            try:
                pdf.drawString(x+264, y-59, str(d.matafuegos.fecha_proxima_carga.month)) #254 #60
                pdf.drawString(x+292, y-58, str(d.matafuegos.fecha_proxima_carga.year)) #282 #60
            except:
                pass
            pdf.drawString(x+337, y-60,str(d.matafuegos.patente)) #327
            pdf.drawString(x+259, y-89, resolve_company_name(d) + "  120")
            y = y-280 #304
            cant -=1
            if cant % 2 == 0 and cant !=0:
                y = 786 #784 # 773
                x = 24 #26 # 50
                pdf.showPage()
                pdf.setFont("Helvetica", 10)
        pdf.save()
        buffer.seek(0)
        messages.success(request, "Informe emitido")
        return FileResponse(buffer, as_attachment=True, filename='oblea_DPS_vehicular.pdf')




#Accion para que emita la información de las DPS domiciliarias
@admin.action(description="Oblea DPS Domiciliaria")
def emitirInformeDPSFijo(self, request, queryset):
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer)
    pdf.setPageSize((6.69291*inch, 12*inch))
    y = 790 #786  # 775
    x = 29 # 52
    pdf.setFont("Helvetica", 10)
    set = queryset.all()
    cant = set.count()
    if set.count() % 2 == 0:
        for d in set:
            if d.estado != 'f' and d.estado != 'i':
                return messages.error(request, 'Orden no finalizada')
        for d in set:
            if not d.fecha_cierre:
                return messages.error(request, f'La orden N° {d.id} no tiene fecha de cierre: no se puede emitir la oblea.')
        for d in set:
            if str(d.matafuegos.categoria) == 'd' and not TareaOrden.objects.filter(orden=d, tarea__es_recarga=True).exists():
                return messages.error(request, f'La orden N° {d.id} no tiene ninguna tarea de recarga: no se puede emitir la oblea.')
        for d in set:
            cant -= 1
            if str(d.matafuegos.categoria) == 'd':
                d.estado = 'i'
                d.save()
                for orden in TareaOrden.objects.filter(orden=d):
                    if orden.tarea.es_recarga:
                        d.matafuegos.fecha_carga = d.fecha_cierre
                    if orden.tarea.nombre == 'Prueba Hidráulica':
                        d.matafuegos.fecha_ph= d.fecha_cierre
                d.matafuegos.numero_dps = d.company.incrementar_dps('dom')
                d.matafuegos.save()
                pdf.drawString(x, y-3, str(d.matafuegos.numero))  # NUMERO DE MATAFUEGO
                pdf.drawString(x+67, y-3, str(d.matafuegos.fecha_fabricacion.year))  # AÑO FABRICACIÓN
                pdf.drawString(x, y-26, resolve_company_name(d))
                pdf.drawString(x+125, y-26, str("120"))
                try:
                    pdf.drawString(x+105, y-3, str(d.matafuegos.fecha_proxima_ph.month)+" "+str(d.matafuegos.fecha_proxima_ph.year))
                except:
                    pass
                pdf.drawString(x+144, y-3,str(d.matafuegos.tipo.volumen))  # CAPACIDAD
                pdf.drawString(x+173, y-3,str(d.matafuegos.tipo))  # AGENTE EXTINTOR
                # ______________
                try:
                    pdf.drawString(x+8, y-65, str(d.matafuegos.fecha_proxima_carga.month))  # Proxima revision recarga mes #59  #67
                    pdf.drawString(x+36, y-65,  str(d.matafuegos.fecha_proxima_carga.year))  # Proxima revision recarga año #59 #67
                except:
                    pass
                pdf.setFont("Helvetica", 7)
                nombre = str(d.matafuegos.cliente.nombre) #Nombre usuario
                if len(nombre) > 22:
                    # Encuentra el índice del último espacio en blanco antes del carácter 21
                    ultimo_espacio = nombre.rfind(' ', 0, 21)

                    if ultimo_espacio != -1:
                        # Divide el nombre en dos partes en el último espacio en blanco
                        primera_parte = nombre[:ultimo_espacio]
                        segunda_parte = nombre[ultimo_espacio + 1:]

                        pdf.drawString(x + 73, y - 54, primera_parte)
                        pdf.drawString(x + 73, y - 64, segunda_parte)
                    else:
                        # Si no se encontró ningún espacio en blanco, simplemente corta el nombre en 21 caracteres
                        pdf.drawString(x + 73, y - 54, nombre[:22])
                        pdf.drawString(x+73, y-64, nombre[22:])
                else:
                    pdf.drawString(x + 73, y - 54, nombre)
                pdf.setFont("Helvetica", 10)
                #Para extintor
                pdf.drawString(x+254, y-28, str(d.matafuegos.numero))#NUMERO DE MATAFUEGO
                try:
                    pdf.drawString(x+312, y-28, str(d.matafuegos.fecha_proxima_ph.month)+ ' ' +str(d.matafuegos.fecha_proxima_ph.year))#venc PH  #24
                except:
                    pass
                try:
                    pdf.drawString(x+256, y-64,str(d.matafuegos.fecha_proxima_carga.month)) #59
                    pdf.drawString(x+286, y-64,str(d.matafuegos.fecha_proxima_carga.year)) #59
                except:
                    pass
                pdf.drawString(x+269, y-90, resolve_company_name(d) + "  120")
                y = y- 284#281 #306  #310 muy abajo #301
            else:
                messages.error(request, "Seleccionar solo categoria domiciliaria")
                return
            if (cant % 2 == 0 and cant !=0):
                    y = 791 #788 #786 #775
                    pdf.showPage()
                    pdf.setFont("Helvetica", 10)
        pdf.showPage()
        pdf.save()
        buffer.seek(0)
        messages.success(request, "Informe emitido")
        return FileResponse(buffer, as_attachment=True, filename='oblea_DPS_domiciliaria.pdf')
    else:
        messages.error(request, "La cantidad de ordenes de trabajo debe ser multiple de dos")

#Accion para que emita el informe de toda la informacion y las tareas de la orden seleccionada
@admin.action(description="Informe Ordenes de trabajo")
def emitirInformeOrden(self, request, queryset):
    set = queryset.all()
    if set.count() != 1:
        messages.error(request, "Seleccionar una orden")
        return
    d = set[0]
    context = report_header_context(d, 'Informe de la orden de trabajo')
    context.update({
        'orden': d,
        'tareas': TareaOrden.objects.filter(orden=d.id),
    })
    pdf_bytes = render_report_pdf('reports/informe_orden.html', context)
    messages.success(request, "Informe emitido")
    return FileResponse(BytesIO(pdf_bytes), as_attachment=True, filename='informe de orden.pdf')

#Informe de las ordenes por cliente para la facturacion
def InformeFacturacion_ultimaSemana(request, ordenes):
    if ordenes.count() < 1:
        return messages.error(request, 'No hay ordenes finalizadas durante la ultima semana')
    grupos = []
    for cliente, ordenes_cliente in groupby(ordenes, key=lambda o: o.cliente):
        filas = []
        for orden in ordenes_cliente:
            tareas = TareaOrden.objects.filter(orden=orden.id)
            for i, t in enumerate(tareas):
                filas.append({'orden': orden, 'tarea': t, 'primera': i == 0})
        if filas:
            grupos.append({'cliente': cliente, 'filas': filas})
    context = report_header_context(ordenes.first(), 'Informe facturación última semana')
    context.update({'grupos': grupos, 'fecha': date.today()})
    pdf_bytes = render_report_pdf('reports/informe_facturacion_semana.html', context)
    messages.success(request, "Informe emitido")
    return FileResponse(BytesIO(pdf_bytes), as_attachment=True, filename='informe_facturacion.pdf')


def _agregar_tareas_por_cliente(ordenes_cliente):
    """Cuenta cuántas veces se repite cada combinación (tarea, cantidad
    cargada, tipo de matafuego) entre las órdenes de un mismo cliente."""
    conteo = {}
    for d in ordenes_cliente:
        tareas = TareaOrden.objects.filter(orden=d.id).order_by('tarea__nombre')
        for t in tareas:
            clave = (t.tarea.nombre, str(t.cant_cargada), str(d.matafuegos.tipo))
            conteo[clave] = conteo.get(clave, 0) + 1
    return conteo


# Informe de factiración por tarea por cliente
@admin.action(description="Informe Facturación")
def InformeFacturacion(self, request, queryset):
    ordenes = queryset.all().order_by('cliente__nombre')
    if ordenes.count() < 1:
        return messages.error(request, ' Debe seleccionar al menos una orden')
    grupos = []
    for cliente, ordenes_cliente in groupby(ordenes, key=lambda o: o.cliente):
        conteo = _agregar_tareas_por_cliente(ordenes_cliente)
        if not conteo:
            continue
        filas = [
            {'cantidad': cantidad, 'tarea': tarea, 'cant_cargada': cant_cargada, 'tipo': tipo}
            for (tarea, cant_cargada, tipo), cantidad in conteo.items()
        ]
        grupos.append({'cliente': cliente, 'filas': filas})
    context = report_header_context(ordenes.first(), 'Informe facturación')
    context.update({'grupos': grupos, 'fecha': date.today()})
    pdf_bytes = render_report_pdf('reports/informe_facturacion.html', context)
    messages.success(request, "Informe emitido")
    return FileResponse(BytesIO(pdf_bytes), as_attachment=True, filename='informe_facturacion.pdf')

class DecadeBornListFilter(admin.SimpleListFilter):
    # Human-readable title which will be displayed in the
    # right admin sidebar just above the filter options.
    title = _('categoria')

    # Parameter for the filter that will be used in the URL query.
    parameter_name = 'matafuegos__categoria'

    def lookups(self, request, model_admin):
        return (
            ('d', _('Domiciliaria')),
            ('v', _('Vehicular')),
        )

    def queryset(self, request, queryset):
        if self.value() == 'v':
            qs= queryset.filter(
                matafuegos__categoria= 'v',
            )
            qs2=queryset.filter(
                matafuegos__categoria= 'ma',
            )
            return qs | qs2

        if self.value() == 'd':
            return queryset.filter(
                matafuegos__categoria= 'd'
            )

class FilterEstado(admin.SimpleListFilter):
    # Filtro para estado
    title = _('estado multiple')

    # Parameter for the filter that will be used in the URL query.
    parameter_name = 'estado'

    def lookups(self, request, model_admin):
        return (
            ('p', _('Pendiente')),
            ('ep', _('En proceso')),
            ('i', _('Impresa')),
            ('fac', _('Facturada')),
            ('f', _('Finalizada')),
            ('c', _('Cancelada')),
            ('fi', _('Finalizada-Impresa'))
        )

    def queryset(self, request, queryset):
        if self.value() == 'fi':
            qs = queryset.filter(
                estado='f',
            )
            qs2 = queryset.filter(
                estado='i',
            )
            return qs | qs2
        if self.value() == 'p':
            qs = queryset.filter(
                estado='p',
            )
            return qs
        if self.value() == 'ep':
            qs = queryset.filter(
                estado='ep',
            )
            return qs
        if self.value() == 'i':
            qs = queryset.filter(
                estado='i',
            )
            return qs
        if self.value() == 'fac':
            qs = queryset.filter(
                estado='fac',
            )
            return qs
        if self.value() == 'f':
            qs = queryset.filter(
                estado='f',
            )
            return qs
        if self.value() == 'c':
            qs = queryset.filter(
                estado='c',
            )
            return qs

class OrdenTrabajoAdmin(CompanyScopedAdmin, admin.ModelAdmin):
    list_display = (
        'id',
        'cliente',
        'matafuegos',
        'get_categoria',
        'estado',
        'fecha_creacion'
    )

    def get_categoria(self, obj):
        if obj.matafuegos.categoria == 'd':
            return 'Domiciliaria'
        return 'Vehicular'
    get_categoria.short_description = 'Categoria'
    autocomplete_fields = ('cliente',)
    search_fields = ('id', 'cliente__codigo', 'cliente__nombre', 'fecha_creacion','matafuegos__numero',)
    list_filter = (DecadeBornListFilter,FilterEstado,)
    inlines = [TareaTabularInline]
    model = Ordenes_de_trabajo
    actions = [action_finalizada, action_facturada, emitirInformeDPSFijo, emitirInformeVehicular,  InformeFacturacion, emitirInformeOrden,'Informe_facturacion_ultimaSemana',]
    ordering = ['-fecha_cierre']
    form = OrdenesTrabajoAdminForm
    list_per_page = 15
    list_max_show_all = 500 # Here

    def save_model(self, request, obj, form, change):
        obj.usuario=request.user.username
        super().save_model(request, obj, form, change)

    def get_readonly_fields(self, request, obj=None):
        if obj is not None and (obj.estado == 'f' or obj.estado == 'c' or obj.estado=='i'):
            OrdenTrabajoAdmin.inlines = [TareaFinalizadaTabularInline]
            return ['id', 'fecha_inicio', 'fecha_entrega', 'fecha_creacion','notas', 'estado', 'monto_total', 'matafuegos','cliente', 'usuario']
        else:
            OrdenTrabajoAdmin.inlines = [TareaTabularInline]
            return ['fecha_inicio','fecha_cierre','monto_total','estado', 'usuario']

    """Funcion para que no sea necesario seleccionar una para el informe de facturacion"""
    def changelist_view(self, request, extra_context=None):
        if 'action' in request.POST and (request.POST['action'] == 'Informe_facturacion_uiltimaSemana'):
            if not request.POST.getlist(ACTION_CHECKBOX_NAME):
                primero = self.get_queryset(request).first()
                if primero is not None:
                    post = request.POST.copy()
                    post.update({ACTION_CHECKBOX_NAME: str(primero.id)})
                    request._set_post(post)
        return super(OrdenTrabajoAdmin, self).changelist_view(request, extra_context)

    @admin.action(description="Informe Facturación ultima semana")
    def Informe_facturacion_ultimaSemana(self, request, obj):
        today = date.today()
        td = timedelta(7)
        ordenes = self.get_queryset(request).filter(estado='i', fecha_cierre__range=(today - td, today)).order_by('cliente')
        return InformeFacturacion_ultimaSemana(request,ordenes)



class TareaOrdenAdmin(admin.ModelAdmin):
    list_display = (
        'tarea',
        'orden'
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

admin.site.register(Ordenes_de_trabajo, OrdenTrabajoAdmin)
admin.site.register(Tarea, TareaAdmin)
admin.site.register(TareaOrden, TareaOrdenAdmin)
