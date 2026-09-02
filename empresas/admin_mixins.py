class CompanyScopedAdmin:
    """Mixin para ModelAdmin de datos operativos (Cliente, Matafuegos, Tarea,
    Ordenes_de_trabajo): un superusuario ve/edita todo; cualquier otro
    usuario (Admin de compañía u Operador) solo ve y solo puede crear/editar
    datos de su propia compañía.

    Medida interina mientras la carga operativa siga disponible desde el
    admin de Django además del portal público (ver plan de fases).
    """

    company_field_name = 'company'

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(**{self.company_field_name: request.user.company})

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if not request.user.is_superuser and hasattr(db_field.related_model, self.company_field_name):
            kwargs['queryset'] = db_field.related_model._default_manager.filter(
                **{self.company_field_name: request.user.company}
            )
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def save_model(self, request, obj, form, change):
        if not request.user.is_superuser:
            setattr(obj, self.company_field_name, request.user.company)
        super().save_model(request, obj, form, change)


class SuperuserOnlyAdminMixin:
    """Mixin para catálogos globales (Marca, Tipo, Categoría de matafuegos):
    solo el superadmin puede verlos/administrarlos desde el admin de Django.
    """

    def has_module_permission(self, request):
        return request.user.is_superuser

    def has_view_permission(self, request, obj=None):
        return request.user.is_superuser

    def has_add_permission(self, request):
        return request.user.is_superuser

    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser
