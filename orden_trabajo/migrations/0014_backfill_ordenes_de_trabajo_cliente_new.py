from django.db import migrations


def backfill_cliente_new(apps, schema_editor):
    OrdenesDeTrabajo = apps.get_model('orden_trabajo', 'Ordenes_de_trabajo')
    Cliente = apps.get_model('cliente', 'Cliente')
    for o in OrdenesDeTrabajo.objects.all():
        cliente = Cliente.objects.get(pk=o.cliente_id)
        o.cliente_new = cliente.cliente_pk
        o.save(update_fields=['cliente_new'])


class Migration(migrations.Migration):

    dependencies = [
        ('orden_trabajo', '0013_ordenes_de_trabajo_cliente_new'),
        ('cliente', '0019_alter_cliente_pk_notnull'),
    ]

    operations = [
        migrations.RunPython(backfill_cliente_new, migrations.RunPython.noop),
    ]
