from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('orden_trabajo', '0016_ordenes_de_trabajo_remove_cliente'),
    ]

    operations = [
        migrations.RenameField(
            model_name='ordenes_de_trabajo',
            old_name='cliente_new',
            new_name='cliente',
        ),
    ]
