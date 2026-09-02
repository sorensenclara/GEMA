from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('matafuegos', '0029_alter_matafuegos_cliente_new_notnull'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='matafuegos',
            name='cliente',
        ),
    ]
