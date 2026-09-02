import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0006_rename_cliente_new_user_cliente'),
        ('cliente', '0024_alter_cliente_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='cliente',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='usuarios_portal',
                to='cliente.cliente',
                help_text='Solo para el rol Cliente final: a qué cliente de la compañía representa este usuario.',
                verbose_name='Cliente asociado',
            ),
        ),
    ]
