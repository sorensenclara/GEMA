from django.contrib.auth.mixins import PermissionRequiredMixin as DjangoPermissionRequiredMixin


class PermissionRequiredMixin(DjangoPermissionRequiredMixin):
    """Thin wrapper around Django's own `PermissionRequiredMixin`, with a
    Spanish denial message matching this project's UI language convention.

    Complementary to `accounts.mixins.RoleRequiredMixin` (and its
    company/role-scoped variants), not a replacement: the role mixins gate
    which portal a user can enter, this mixin is for punctual, non-CRUD
    permissions declared via a model's `Meta.permissions` when a check
    narrower than "has this role" is needed.

    `raise_exception = True` is deliberate: an authenticated user who lacks
    the permission gets an actual 403, not a silent redirect back to login.
    """
    raise_exception = True

    def get_permission_denied_message(self):
        return self.permission_denied_message or "No tiene permisos para acceder a esta sección."
