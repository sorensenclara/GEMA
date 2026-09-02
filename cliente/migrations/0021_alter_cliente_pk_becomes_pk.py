from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cliente', '0020_alter_cliente_codigo_drop_pk'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cliente',
            name='cliente_pk',
            field=models.BigAutoField(primary_key=True, serialize=False),
        ),
        # Django crea la secuencia de la nueva PK arrancando en 1; como la
        # columna ya tenía valores backfillados (1..N), hay que adelantar la
        # secuencia al máximo actual o el próximo INSERT choca con un id
        # existente.
        migrations.RunSQL(
            sql="SELECT setval(pg_get_serial_sequence('cliente_cliente', 'cliente_pk'), "
                "COALESCE((SELECT MAX(cliente_pk) FROM cliente_cliente), 1));",
            reverse_sql=migrations.RunSQL.noop,
        ),
    ]
