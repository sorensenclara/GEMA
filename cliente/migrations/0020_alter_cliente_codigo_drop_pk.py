from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cliente', '0019_alter_cliente_pk_notnull'),
        # Las tres FKs que apuntaban a codigo ya fueron repuntadas a cliente_pk;
        # solo entonces es seguro sacarle la restricción de PK a codigo.
        ('matafuegos', '0031_rename_cliente_new_matafuegos_cliente'),
        ('orden_trabajo', '0017_rename_cliente_new_ordenes_de_trabajo_cliente'),
        ('accounts', '0006_rename_cliente_new_user_cliente'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cliente',
            name='codigo',
            field=models.CharField(max_length=50, verbose_name='Codigo'),
        ),
    ]
