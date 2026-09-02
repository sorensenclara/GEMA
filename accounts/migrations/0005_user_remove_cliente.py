from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0004_backfill_user_cliente_new'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='cliente',
        ),
    ]
