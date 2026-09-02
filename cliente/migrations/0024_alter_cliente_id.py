from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cliente', '0023_cliente_company_codigo_unique'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cliente',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
    ]
