from django.db import migrations, models


class Migration(migrations.Migration):
    """Columna puente (entero simple, sin FK todavía) que va a terminar
    guardando el futuro id de Cliente. Se crea sin FK a propósito: una FK real
    acá generaría una constraint que dependería del índice único de
    `cliente.cliente_pk`, y esa dependencia impediría luego convertir
    `cliente_pk` en primary key (Postgres no permite dropear un índice del que
    depende una FK). La conversión a FK real ocurre recién en la migración
    final, una vez que `cliente.id` ya es la primary key definitiva.
    """

    dependencies = [
        ('matafuegos', '0026_alter_matafuegos_company_notnull'),
    ]

    operations = [
        migrations.AddField(
            model_name='matafuegos',
            name='cliente_new',
            field=models.BigIntegerField(null=True),
        ),
    ]
