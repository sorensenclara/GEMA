from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0005_user_remove_cliente'),
    ]

    operations = [
        migrations.RenameField(
            model_name='user',
            old_name='cliente_new',
            new_name='cliente',
        ),
    ]
