from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cliente', '0018_backfill_cliente_pk'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cliente',
            name='cliente_pk',
            field=models.BigIntegerField(unique=True),
        ),
    ]
