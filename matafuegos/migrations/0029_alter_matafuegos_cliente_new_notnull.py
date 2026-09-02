from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('matafuegos', '0028_backfill_matafuegos_cliente_new'),
    ]

    operations = [
        migrations.AlterField(
            model_name='matafuegos',
            name='cliente_new',
            field=models.BigIntegerField(),
        ),
    ]
