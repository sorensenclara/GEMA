from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orden_trabajo', '0014_backfill_ordenes_de_trabajo_cliente_new'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ordenes_de_trabajo',
            name='cliente_new',
            field=models.BigIntegerField(),
        ),
    ]
