from django.db import migrations


def marcar_recarga(apps, schema_editor):
    """El sistema original identificaba la tarea de recarga por nombre
    exacto ('Control y mantenimiento') para actualizar fecha_carga al
    imprimir la oblea DPS. Ahora que Tarea es un catálogo libre por
    compañía, esa distinción pasa a ser un campo explícito; para no romper
    compañías que ya tenían esa tarea cargada, se la marca automáticamente."""
    Tarea = apps.get_model('orden_trabajo', 'Tarea')
    Tarea.objects.filter(nombre__iexact='Control y mantenimiento').update(es_recarga=True)


class Migration(migrations.Migration):

    dependencies = [
        ('orden_trabajo', '0020_tarea_es_recarga'),
    ]

    operations = [
        migrations.RunPython(marcar_recarga, migrations.RunPython.noop),
    ]
