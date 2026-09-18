from django.contrib import admin

from .models import Company


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'is_active', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('nombre',)
    fieldsets = (
        (None, {'fields': ('nombre', 'logo', 'is_active', 'numero_recargador')}),
        ('Numeración DPS', {
            'fields': (
                ('veh_prefijo', 'veh_inicio', 'veh_fin', 'veh_actual'),
                ('dom_prefijo', 'dom_inicio', 'dom_fin', 'dom_actual'),
            ),
        }),
        ('Envío de informes (SMTP)', {'fields': ('smtp_email', 'smtp_password')}),
    )

    def has_module_permission(self, request):
        # La creación/administración de compañías es exclusiva del superadmin,
        # desde este admin o las vistas dedicadas (ver empresas/views/company_admin.py).
        return request.user.is_superuser

    def has_view_permission(self, request, obj=None):
        return request.user.is_superuser

    def has_add_permission(self, request):
        return request.user.is_superuser

    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser
