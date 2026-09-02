from datetime import date, timedelta
from io import BytesIO
from itertools import groupby
from django.contrib import admin, messages
from django.contrib.admin.helpers import ACTION_CHECKBOX_NAME
from django.db.models import Q
from django.http import FileResponse
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from .models import CategoriaMatafuegos, TipoMatafuegos, MarcaMatafuegos, Matafuegos
from django.shortcuts import render, redirect
from empresas.admin_mixins import CompanyScopedAdmin, SuperuserOnlyAdminMixin
from reports.branding import report_header_context
from reports.pdf_render import render_report_pdf


def _agrupar_por_cliente(queryset):
    return [
        {'cliente': cliente, 'items': list(items)}
        for cliente, items in groupby(queryset, key=lambda d: d.cliente)
    ]

def generarListadoMatafuegos(queryset):
    matafuegos = list(queryset)
    context = report_header_context(matafuegos[0] if matafuegos else None, 'Listado de matafuegos')
    context['matafuegos'] = matafuegos
    return render_report_pdf('reports/listado_matafuegos.html', context)

"""Escritura del informe alerta de los proximos vencimientos tabla completa"""
def emitirAlerta(self,request,lista, fechaI, fechaF):
        if len(lista) < 1:
            return messages.error(request,'No hay matafuegos con vencimiento entre las fechas')
        context = report_header_context(lista[0], 'Alerta de vencimientos')
        context.update({'lista': lista, 'fecha_inicio': fechaI, 'fecha_fin': fechaF})
        pdf_bytes = render_report_pdf('reports/alerta_vencimientos.html', context)
        messages.success(request, "Informe emitido")
        return FileResponse(BytesIO(pdf_bytes), as_attachment=True, filename='alerta_vencimientos.pdf')

class MatafuegosResource(resources.ModelResource):

    class Meta:
        model = Matafuegos

class MatafuegosAdmin(CompanyScopedAdmin, ImportExportModelAdmin):
    list_display = (
        'numero',
        'cliente',
        'fecha_proxima_carga',
        'fecha_proxima_ph',
        'vencido',
    )
    search_fields= ('cliente__nombre','numero', 'numero_dps',)
    list_filter= ('categoria','vencido')
    actions = ['vencimientos_fechas','proximos_vencimientos','alerta_vencimientos']
    readonly_fields=['fecha_proxima_carga','fecha_proxima_ph',]
    resource_class = MatafuegosResource
    autocomplete_fields = ['cliente']
    list_per_page = 15
    list_max_show_all = 500

    """ Acción para el informe de los vencimiento entre 2 fechas"""
    def vencimientos_fechas(self, request, queryset):
        if 'apply' in request.POST:
            fechaInicio= request.POST['inicio']
            fechafin=request.POST['fin']
            if fechaInicio > fechafin:
                messages.error(request,'La fecha de fin debe ser mayor a la de inicio')
                return render(request,
                      'order_intermediate.html',
                      context={})
            if not fechaInicio:
               messages.error(request,'Especificar fehca de inicio')
            if not fechafin:
               messages.error(request,'Especificar fehca de fin')
            if fechaInicio and fechafin:
                filtroC = self.get_queryset(request).filter(Q(fecha_proxima_carga__range=(fechaInicio, fechafin))).order_by('categoria','cliente__nombre')
                return emitirAlerta(self,request,filtroC, fechaInicio, fechafin)
        if 'volver' in request.POST:
            return
        return render(request,
                      'order_intermediate.html',
                      context={})

    vencimientos_fechas.short_description = "Vencimientos por fecha"

    """Funcion para que no sea necesario seleccionar un matafuego para la accion proximos-vencimientos"""
    def changelist_view(self, request, extra_context=None):
        if 'action' in request.POST and (request.POST['action'] == 'proximos_vencimientos' or request.POST['action'] == 'alerta_vencimientos' or request.POST['action'] == 'vencimientos_fechas' ):
            if not request.POST.getlist(ACTION_CHECKBOX_NAME):
                primero = self.get_queryset(request).first()
                if primero is not None:
                    post = request.POST.copy()
                    post.update({ACTION_CHECKBOX_NAME: str(primero.id)})
                    request._set_post(post)
        return super(MatafuegosAdmin, self).changelist_view(request, extra_context)

    """Accion para emitir los vencimientos de carga y ph del proximo mes"""
    @admin.action(description="Informe proximos vencimientos a 30 dias")
    def proximos_vencimientos(self, request, obj):
        today = date.today()
        td = timedelta(30)
        filtroC = self.get_queryset(request).filter(Q(fecha_proxima_carga__range=(today, today + td))).order_by('categoria','cliente__nombre')
        filtroP = self.get_queryset(request).filter(Q(fecha_proxima_ph__range=(today,today + td))).order_by('categoria','cliente__nombre')
        return self.emitirInforme(request,filtroC,filtroP)

    """Escritura del informe de los proximos vencimientos separado por cliente"""
    def emitirInforme(self,request, carga,ph):
        if carga.count() < 1 and ph.count() < 1:
            return messages.error(request,'No hay matafuegos con vencimiento en los proximos 30 dias')
        primero = carga.first() or ph.first()
        context = report_header_context(primero, 'Próximos vencimientos')
        context.update({
            'grupos_carga': _agrupar_por_cliente(carga),
            'grupos_ph': _agrupar_por_cliente(ph),
        })
        pdf_bytes = render_report_pdf('reports/proximos_vencimientos.html', context)
        messages.success(request, "Informe emitido")
        return FileResponse(BytesIO(pdf_bytes), as_attachment=True, filename='proximos_vencimientos.pdf')

    #----------------------------------------------------------------------------------------------


    """Accion para emitir los vencimientos de carga del proximo mes"""
    @admin.action(description="Alerta de vencimientos a 30 dias")
    def alerta_vencimientos(self, request, obj):
        today = date.today()
        td = timedelta(30)
        filtroC = self.get_queryset(request).filter(Q(fecha_proxima_carga__range=(today, today + td))).order_by('categoria','cliente__nombre')
        return emitirAlerta(self,request,filtroC, str(today), str(today +td))



class TipoMatafuegosAdmin(SuperuserOnlyAdminMixin, admin.ModelAdmin):
    list_display = (
        'tipo',
        'categoria',
        'vencimiento_carga',
        'vencimiento_ph',
        'volumen',
        'peso',
    )
    search_fields= ('tipo',)
    list_filter= ('categoria',)

class CategoriaMatafuegosAdmin(SuperuserOnlyAdminMixin, admin.ModelAdmin):
    pass

class MarcaMatafuegosAdmin(SuperuserOnlyAdminMixin, admin.ModelAdmin):
    pass

# Marca/Tipo/Categoría de matafuegos son catálogos globales, comunes a todas
# las compañías: solo el superadmin puede administrarlos (ver plan de fases).
admin.site.register(CategoriaMatafuegos, CategoriaMatafuegosAdmin)
admin.site.register(TipoMatafuegos, TipoMatafuegosAdmin)
admin.site.register(MarcaMatafuegos, MarcaMatafuegosAdmin)
admin.site.register(Matafuegos, MatafuegosAdmin)
