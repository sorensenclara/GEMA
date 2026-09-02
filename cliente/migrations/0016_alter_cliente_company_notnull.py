import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('empresas', '0002_create_initial_company'),
        ('cliente', '0015_cliente_company'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cliente',
            name='company',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='clientes', to='empresas.company', verbose_name='Compañía'),
        ),
    ]
