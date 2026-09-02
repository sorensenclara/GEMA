from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cliente', '0022_rename_cliente_pk_id'),
    ]

    operations = [
        migrations.AddConstraint(
            model_name='cliente',
            constraint=models.UniqueConstraint(fields=['company', 'codigo'], name='cliente_company_codigo_unique'),
        ),
    ]
