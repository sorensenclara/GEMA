from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cliente', '0021_alter_cliente_pk_becomes_pk'),
    ]

    operations = [
        migrations.RenameField(
            model_name='cliente',
            old_name='cliente_pk',
            new_name='id',
        ),
    ]
