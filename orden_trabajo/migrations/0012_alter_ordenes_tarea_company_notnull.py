import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('empresas', '0002_create_initial_company'),
        ('orden_trabajo', '0011_ordenes_de_trabajo_company_tarea_company'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ordenes_de_trabajo',
            name='company',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='ordenes_de_trabajo', to='empresas.company', verbose_name='Compañía'),
        ),
        migrations.AlterField(
            model_name='tarea',
            name='company',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='tareas', to='empresas.company', verbose_name='Compañía'),
        ),
    ]
