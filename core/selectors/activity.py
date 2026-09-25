from django.apps import apps

# Qué modelos entran en "Actividad reciente" del dashboard y cómo se
# etiqueta cada uno -- vive acá (no en cada app) porque ninguno de los 4
# modelos conoce a los otros; mismo criterio que el historial genérico de
# core/selectors/history.py (que sí opera sobre UN objeto ya identificado,
# en vez de mezclar varios modelos por fecha como hace esta función).
_MODELOS_ACTIVIDAD = [
    {'app_label': 'cliente', 'model_name': 'cliente', 'label': 'Cliente'},
    {'app_label': 'matafuegos', 'model_name': 'matafuegos', 'label': 'Matafuego'},
    {'app_label': 'orden_trabajo', 'model_name': 'ordenes_de_trabajo', 'label': 'Orden de trabajo'},
    {'app_label': 'orden_trabajo', 'model_name': 'tarea', 'label': 'Tarea'},
]

# history_type de django-simple-history: '+' alta, '~' modificación, '-' baja.
_ACCION_POR_TIPO = {
    '+': 'creado',
    '~': 'actualizado',
    '-': 'eliminado',
}

# Clases badge-activity-* ya definidas en theme.css (tabla de Actividad
# reciente): una por tipo de acción, igual para cualquier modelo.
_BADGE_POR_TIPO = {
    '+': 'badge-activity-purple',
    '~': 'badge-activity-info',
    '-': 'badge-activity-danger',
}


def recent_activity(company, limit=15):
    """Actividad reciente de la compañía: últimas altas/modificaciones/bajas
    sobre Cliente, Matafuego, Orden de trabajo y Tarea, mezcladas por fecha.

    No existe una forma de pedirle a la base un solo listado ordenado entre
    tablas de modelos distintos (cada uno tiene su propia tabla histórica de
    django-simple-history), así que se traen hasta `limit` filas de cada
    modelo (ya ordenadas por fecha) y se mezclan acá en Python, quedándonos
    con las `limit` más recientes en total. Con 4 modelos y un límite chico
    esto no pesa, incluso sin esa optimización.

    Simplificación consciente (a revisar si hace falta más adelante): no se
    intenta describir el cambio de negocio puntual (ej. "orden finalizada",
    "cliente reactivado") -- eso requeriría diffear cada modelo por separado
    -- se muestra en cambio "<Modelo> creado/actualizado/eliminado" + la
    descripción del objeto en ese momento (su propio __str__).
    """
    filas = []
    for meta in _MODELOS_ACTIVIDAD:
        model = apps.get_model(meta['app_label'], meta['model_name'])
        pk_field = model._meta.pk.attname
        historial = (
            model.history.filter(company_id=company.pk)
            .select_related('history_user')
            .order_by('-history_date')[:limit]
        )
        for record in historial:
            eliminado = record.history_type == '-'
            filas.append({
                'timestamp': record.history_date,
                'usuario': record.history_user,
                'accion': _ACCION_POR_TIPO.get(record.history_type, record.history_type),
                'badge_class': _BADGE_POR_TIPO.get(record.history_type, 'badge-activity-info'),
                'modelo_label': meta['label'],
                'descripcion': str(record),
                # El historial genérico (core:history) hace get_object_or_404
                # sobre el modelo ACTUAL, no sobre la fila histórica -- un
                # objeto eliminado ya no existe ahí, así que esas filas no
                # llevan link (mismo criterio que "Tareas demoradas" en
                # Requieren atención, que tampoco linkea a nada todavía).
                'app_label': None if eliminado else meta['app_label'],
                'model_name': None if eliminado else meta['model_name'],
                'object_pk': None if eliminado else getattr(record, pk_field),
            })

    filas.sort(key=lambda fila: fila['timestamp'], reverse=True)
    return filas[:limit]
