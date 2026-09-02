import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('empresas', '0001_initial'),
        ('cliente', '0014_alter_cliente_codigo'),
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='role',
            field=models.CharField(blank=True, choices=[('admin_empresa', 'Admin de compañía'), ('operador', 'Operador'), ('cliente_final', 'Cliente final')], max_length=20, verbose_name='Rol'),
        ),
        migrations.AddField(
            model_name='user',
            name='company',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='usuarios', to='empresas.company', verbose_name='Compañía'),
        ),
        migrations.AddField(
            model_name='user',
            name='cliente',
            field=models.ForeignKey(blank=True, help_text='Solo para el rol Cliente final: a qué cliente de la compañía representa este usuario.', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='usuarios_portal', to='cliente.cliente', verbose_name='Cliente asociado'),
        ),
    ]
