from django.db import migrations


def backfill_cliente_new(apps, schema_editor):
    User = apps.get_model('accounts', 'User')
    Cliente = apps.get_model('cliente', 'Cliente')
    for u in User.objects.filter(cliente__isnull=False):
        cliente = Cliente.objects.get(pk=u.cliente_id)
        u.cliente_new = cliente.cliente_pk
        u.save(update_fields=['cliente_new'])


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0003_user_cliente_new'),
        ('cliente', '0019_alter_cliente_pk_notnull'),
    ]

    operations = [
        migrations.RunPython(backfill_cliente_new, migrations.RunPython.noop),
    ]
