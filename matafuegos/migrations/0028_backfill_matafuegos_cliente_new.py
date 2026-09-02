from django.db import migrations


def backfill_cliente_new(apps, schema_editor):
    Matafuegos = apps.get_model('matafuegos', 'Matafuegos')
    Cliente = apps.get_model('cliente', 'Cliente')
    for m in Matafuegos.objects.all():
        cliente = Cliente.objects.get(pk=m.cliente_id)
        m.cliente_new = cliente.cliente_pk
        m.save(update_fields=['cliente_new'])


class Migration(migrations.Migration):

    dependencies = [
        ('matafuegos', '0027_matafuegos_cliente_new'),
        ('cliente', '0019_alter_cliente_pk_notnull'),
    ]

    operations = [
        migrations.RunPython(backfill_cliente_new, migrations.RunPython.noop),
    ]
