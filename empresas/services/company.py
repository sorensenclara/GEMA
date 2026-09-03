from django.db import models, transaction
from django.utils.crypto import get_random_string

from accounts.models import Role, User
from accounts.services import invitar_usuario
from empresas.exceptions import RangoDpsAgotadoException
from empresas.models import Company


def incrementar_dps(company, serie, paso=2):
    """Asigna atómicamente el próximo número de DPS de la serie ('veh' u 'dom')
    y devuelve el valor ya formateado con su prefijo."""
    assert serie in ('veh', 'dom')
    campo_actual = f'{serie}_actual'
    campo_fin = f'{serie}_fin'
    campo_prefijo = f'{serie}_prefijo'
    with transaction.atomic():
        row = Company.objects.select_for_update().get(pk=company.pk)
        actual = getattr(row, campo_actual)
        fin = getattr(row, campo_fin)
        if fin and actual + paso > fin:
            raise RangoDpsAgotadoException(
                f'El rango de numeración DPS "{serie}" de "{row.nombre}" está agotado '
                f'(próximo número {actual + paso} supera el límite configurado {fin}).'
            )
        valor_impreso = f"{getattr(row, campo_prefijo)}{actual}"
        Company.objects.filter(pk=company.pk).update(
            **{campo_actual: models.F(campo_actual) + paso}
        )
    company.refresh_from_db(fields=[campo_actual])
    return valor_impreso


def crear_company_con_admin(company, admin_username, admin_email, domain, use_https):
    """Crea la compañía junto con su primer usuario (Admin de compañía) e
    inicia el flujo de invitación por email para que defina su contraseña.
    `domain`/`use_https` reemplazan a `request` -- ver PasswordResetForm.save()."""
    with transaction.atomic():
        company.save()
        admin_user = User(
            username=admin_username,
            email=admin_email,
            company=company,
            role=Role.ADMIN_EMPRESA,
        )
        admin_user.set_password(get_random_string(32))
        admin_user.save()

    invitar_usuario(admin_user, domain=domain, use_https=use_https)
    return company, admin_user
