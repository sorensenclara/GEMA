from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cliente', '0016_alter_cliente_company_notnull'),
    ]

    operations = [
        migrations.AddField(
            model_name='cliente',
            name='cliente_pk',
            field=models.BigIntegerField(null=True, unique=True),
        ),
    ]
