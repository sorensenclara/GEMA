from django.db import migrations


def quitar_is_staff_no_superusers(apps, schema_editor):
    User = apps.get_model('accounts', 'User')
    User.objects.filter(is_superuser=False, is_staff=True).update(is_staff=False)


class Migration(migrations.Migration):
    """La carga operativa (clientes/matafuegos/tareas/órdenes) y la gestión
    de usuarios ahora se hacen desde el portal público, no desde el admin de
    Django. Solo el superadmin conserva acceso al admin."""

    dependencies = [
        ('accounts', '0007_alter_user_cliente_final'),
    ]

    operations = [
        migrations.RunPython(quitar_is_staff_no_superusers, migrations.RunPython.noop),
    ]
