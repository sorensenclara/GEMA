from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('matafuegos', '0030_matafuegos_remove_cliente'),
    ]

    operations = [
        migrations.RenameField(
            model_name='matafuegos',
            old_name='cliente_new',
            new_name='cliente',
        ),
    ]
