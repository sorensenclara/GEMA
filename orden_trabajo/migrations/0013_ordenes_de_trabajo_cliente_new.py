from django.db import migrations, models


class Migration(migrations.Migration):
    """Ver la nota en matafuegos/migrations/0027_matafuegos_cliente_new.py:
    columna puente sin FK todavía, para no bloquear la promoción de
    `cliente.cliente_pk` a primary key.
    """

    dependencies = [
        ('orden_trabajo', '0012_alter_ordenes_tarea_company_notnull'),
    ]

    operations = [
        migrations.AddField(
            model_name='ordenes_de_trabajo',
            name='cliente_new',
            field=models.BigIntegerField(null=True),
        ),
    ]
