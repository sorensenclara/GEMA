from django.contrib import admin

# Register your models here.
from .models import Parametros


class ParametrosAdmin(admin.ModelAdmin):
    list_display = (
        'veh_inicio',
        'veh_fin',
        'veh_prefijo',
        'veh_actual',
        'dom_inicio',
        'dom_fin',
        'dom_prefijo',
        'dom_actual',
    )

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


admin.site.register(Parametros, ParametrosAdmin)
