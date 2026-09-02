from django.db import migrations


def backfill_cliente_pk(apps, schema_editor):
    Cliente = apps.get_model('cliente', 'Cliente')
    for i, cliente in enumerate(Cliente.objects.order_by('codigo'), start=1):
        cliente.cliente_pk = i
        cliente.save(update_fields=['cliente_pk'])


class Migration(migrations.Migration):

    dependencies = [
        ('cliente', '0017_cliente_cliente_pk'),
    ]

    operations = [
        migrations.RunPython(backfill_cliente_pk, migrations.RunPython.noop),
    ]
