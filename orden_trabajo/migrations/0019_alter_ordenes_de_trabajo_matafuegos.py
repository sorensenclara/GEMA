from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('matafuegos', '0032_alter_matafuegos_cliente_final'),
        ('orden_trabajo', '0018_alter_ordenes_de_trabajo_cliente_final'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ordenes_de_trabajo',
            name='matafuegos',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ordenes_de_trabajo', to='matafuegos.matafuegos', verbose_name='Matafuegos'),
        ),
    ]
