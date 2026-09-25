# Migración de datos: marca a los clientes que ya existían en GEMA antes de
# esta funcionalidad como "manual_legado", sin tocar su campo `direccion`
# ni ningún otro dato. No se llama al servicio de geocodificación (sin
# búsquedas masivas, tal como se acordó con Clara, 2026-09-23).
from django.db import migrations


def marcar_como_legado(apps, schema_editor):
    Cliente = apps.get_model('cliente', 'Cliente')
    Cliente.objects.filter(geo_status__isnull=True).update(geo_status='manual_legado')


def revertir(apps, schema_editor):
    # No hay nada que "deshacer" de forma segura: bajar la migración
    # deja geo_status como estaba (nulo) para quien lo necesite, sin
    # intentar adivinar qué filas fueron tocadas por esta migración
    # y cuáles no.
    Cliente = apps.get_model('cliente', 'Cliente')
    Cliente.objects.filter(geo_status='manual_legado').update(geo_status=None)


class Migration(migrations.Migration):

    dependencies = [
        ('cliente', '0026_cliente_codigo_postal_cliente_geo_provider_and_more'),
    ]

    operations = [
        migrations.RunPython(marcar_como_legado, revertir),
    ]
