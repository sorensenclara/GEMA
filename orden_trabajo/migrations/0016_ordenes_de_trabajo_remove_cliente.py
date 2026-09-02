from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('orden_trabajo', '0015_alter_ordenes_de_trabajo_cliente_new_notnull'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='ordenes_de_trabajo',
            name='cliente',
        ),
    ]
