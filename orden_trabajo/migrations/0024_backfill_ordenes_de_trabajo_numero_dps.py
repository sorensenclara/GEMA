"""Reconstruye, a partir del historial de auditoria de Matafuegos
(django-simple-history), el N° de DPS que le correspondio a cada orden de
recarga ya emitida antes de que existiera Ordenes_de_trabajo.numero_dps.

`Matafuegos.numero_dps` es de solo lectura una vez creado el matafuego (ver
matafuegos/forms/matafuegos.py) -- el unico lugar que lo modifica despues de
la creacion es `_actualizar_matafuego_y_marcar_impresa` en
orden_trabajo/services/oblea.py, exactamente una vez por orden de recarga
emitida. Esto permite emparejar, para cada matafuego y en orden cronologico,
cada cambio de numero_dps en el historial con la orden de recarga
correspondiente. Es un best-effort: si el historial fue purgado o hay
discrepancias, algunas ordenes viejas quedaran sin numero_dps (se
completaran solas hacia adelante)."""
from django.db import migrations


def backfill_numero_dps(apps, schema_editor):
    Matafuegos = apps.get_model('matafuegos', 'Matafuegos')
    HistoricalMatafuegos = apps.get_model('matafuegos', 'HistoricalMatafuegos')
    OrdenesDeTrabajo = apps.get_model('orden_trabajo', 'Ordenes_de_trabajo')
    TareaOrden = apps.get_model('orden_trabajo', 'TareaOrden')

    ordenes_de_recarga_ids = TareaOrden.objects.filter(tarea__es_recarga=True).values('orden_id')

    for matafuego_id in Matafuegos.objects.values_list('pk', flat=True):
        ordenes = list(
            OrdenesDeTrabajo.objects
            .filter(matafuegos_id=matafuego_id, estado__in=('i', 'fac'), pk__in=ordenes_de_recarga_ids)
            .order_by('fecha_cierre', 'id')
        )
        if not ordenes:
            continue

        historial = list(HistoricalMatafuegos.objects.filter(id=matafuego_id).order_by('history_date'))
        valores_dps = []
        anterior = historial[0].numero_dps if historial else None
        for registro in historial[1:]:
            if registro.numero_dps != anterior:
                valores_dps.append(registro.numero_dps)
                anterior = registro.numero_dps

        for orden, numero_dps in zip(ordenes, valores_dps):
            orden.numero_dps = numero_dps
            orden.save(update_fields=['numero_dps'])


class Migration(migrations.Migration):

    dependencies = [
        ('orden_trabajo', '0023_ordenes_de_trabajo_numero_dps'),
        ('matafuegos', '0034_historicalmatafuegos_estado_matafuegos_estado'),
    ]

    operations = [
        migrations.RunPython(backfill_numero_dps, migrations.RunPython.noop),
    ]
