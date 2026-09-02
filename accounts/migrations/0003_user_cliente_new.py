from django.db import migrations, models


class Migration(migrations.Migration):
    """Ver la nota en matafuegos/migrations/0027_matafuegos_cliente_new.py:
    columna puente sin FK todavía, para no bloquear la promoción de
    `cliente.cliente_pk` a primary key.
    """

    dependencies = [
        ('accounts', '0002_user_company_role_cliente'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='cliente_new',
            field=models.BigIntegerField(null=True),
        ),
    ]
