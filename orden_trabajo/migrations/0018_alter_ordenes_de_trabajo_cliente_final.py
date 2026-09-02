import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orden_trabajo', '0017_rename_cliente_new_ordenes_de_trabajo_cliente'),
        ('cliente', '0024_alter_cliente_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ordenes_de_trabajo',
            name='cliente',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='ordenes_de_trabajo',
                to='cliente.cliente',
                verbose_name='Cliente',
            ),
        ),
    ]
