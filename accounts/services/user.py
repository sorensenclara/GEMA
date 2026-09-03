from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.tokens import default_token_generator

from accounts.exceptions import NoPuedeDesactivarsePropioUsuarioException


def invitar_usuario(user, domain, use_https):
    """Envía el email de invitación (definir contraseña) a un usuario recién
    creado. `domain`/`use_https` reemplazan a `request` -- ver
    PasswordResetForm.save(). No hace nada si el usuario no tiene email
    cargado."""
    if not user.email:
        return False
    form = PasswordResetForm({'email': user.email})
    if not form.is_valid():
        return False
    form.save(
        domain_override=domain,
        use_https=use_https,
        email_template_name='registration/invite_email.txt',
        subject_template_name='registration/invite_subject.txt',
        token_generator=default_token_generator,
    )
    return True


def desactivar_usuario(user, acting_user):
    """El único caso de negocio no trivial de esta app: sin este chequeo, un
    usuario con acceso a la gestión de usuarios de su compañía podría
    desactivar su propia cuenta y quedar bloqueado sin que nadie más de su
    compañía pueda reactivarlo."""
    if user.pk == acting_user.pk:
        raise NoPuedeDesactivarsePropioUsuarioException('No puede desactivar su propio usuario.')
    user.is_active = False
    user.save(update_fields=['is_active'])
    return user


def activar_usuario(user):
    user.is_active = True
    user.save(update_fields=['is_active'])
    return user
