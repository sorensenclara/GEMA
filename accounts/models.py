from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models


class Role(models.TextChoices):
    ADMIN_EMPRESA = 'admin_empresa', 'Admin de compañía'
    OPERADOR = 'operador', 'Operador'
    CLIENTE_FINAL = 'cliente_final', 'Cliente final'


class User(AbstractUser):
    company = models.ForeignKey(
        'empresas.Company', verbose_name='Compañía', null=True, blank=True,
        on_delete=models.PROTECT, related_name='usuarios',
    )
    role = models.CharField('Rol', max_length=20, choices=Role.choices, blank=True)
    cliente = models.ForeignKey(
        'cliente.Cliente', verbose_name='Cliente asociado', null=True, blank=True,
        on_delete=models.SET_NULL, related_name='usuarios_portal',
        help_text='Solo para el rol Cliente final: a qué cliente de la compañía representa este usuario.',
    )

    class Meta:
        # Mantiene el nombre físico de tabla de django.contrib.auth.models.User.
        # Como esta migración inicial no agrega columnas nuevas (company/role/cliente
        # se agregan en una migración posterior), en un despliegue que ya tenía la
        # tabla auth_user con datos reales, la migración 0001 de esta app se aplica
        # con `migrate accounts 0001 --fake` (la tabla ya existe con la misma
        # estructura); en una base nueva, se crea normalmente sin pasos especiales.
        db_table = 'auth_user'

    @property
    def is_superadmin(self):
        return self.is_superuser

    @property
    def is_company_admin(self):
        return self.role == Role.ADMIN_EMPRESA

    @property
    def is_operador(self):
        return self.role == Role.OPERADOR

    @property
    def is_cliente_final(self):
        return self.role == Role.CLIENTE_FINAL

    def clean(self):
        super().clean()
        if self.is_superuser:
            return
        if not self.company_id:
            raise ValidationError('Todo usuario que no sea superadmin debe pertenecer a una compañía.')
        if not self.role:
            raise ValidationError('Debe indicar un rol para el usuario.')
        if self.role == Role.CLIENTE_FINAL:
            if not self.cliente_id:
                raise ValidationError('Un usuario Cliente final debe tener un cliente asociado.')
            if self.cliente.company_id != self.company_id:
                raise ValidationError('El cliente asociado debe pertenecer a la misma compañía que el usuario.')
        elif self.cliente_id:
            raise ValidationError('Solo los usuarios Cliente final pueden tener un cliente asociado.')
