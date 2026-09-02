from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from .models import User


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    fieldsets = DjangoUserAdmin.fieldsets + (
        ('Compañía', {'fields': ('company', 'role', 'cliente')}),
    )
    add_fieldsets = DjangoUserAdmin.add_fieldsets + (
        ('Compañía', {'fields': ('company', 'role', 'cliente')}),
    )
    list_display = DjangoUserAdmin.list_display + ('company', 'role')
    list_filter = DjangoUserAdmin.list_filter + ('company', 'role')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(company=request.user.company)

    def has_module_permission(self, request):
        # La gestión de usuarios de cada compañía se hace desde el portal
        # público, no desde el admin de Django (ver app `portal`).
        return request.user.is_superuser
