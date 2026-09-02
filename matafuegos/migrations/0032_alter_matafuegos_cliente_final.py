import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    """Convierte la columna puente (entero simple) en una FK real hacia
    Cliente, ahora que `cliente.id` ya es la primary key definitiva. Recién
    acá se crea la constraint de FK, evitando el problema de dependencias
    descripto en 0027_matafuegos_cliente_new.
    """

    dependencies = [
        ('matafuegos', '0031_rename_cliente_new_matafuegos_cliente'),
        ('cliente', '0024_alter_cliente_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='matafuegos',
            name='cliente',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.RESTRICT,
                related_name='matafuegos',
                to='cliente.cliente',
                verbose_name='Cliente',
            ),
        ),
    ]
