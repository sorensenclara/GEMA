from datetime import date, timedelta

from django.db.models import Q

from matafuegos.models import Matafuegos


def list_matafuegos(company, q=None, tipo=None, estado=None, vencido=None):
    qs = Matafuegos.objects.filter(company=company).select_related('cliente', 'tipo').order_by('numero')
    if q:
        qs = qs.filter(Q(numero__icontains=q) | Q(cliente__nombre__icontains=q) | Q(numero_dps__icontains=q))
    if tipo:
        qs = qs.filter(tipo_id=tipo)
    if estado:
        qs = qs.filter(estado=estado)
    if vencido:
        qs = qs.filter(vencido=vencido == '1')
    return qs


def list_vencimiento_entre(company, fecha_inicio, fecha_fin):
    return Matafuegos.objects.filter(
        company=company, fecha_proxima_carga__range=(fecha_inicio, fecha_fin),
    ).order_by('categoria', 'cliente__nombre')


def list_proximos_vencimientos_carga(company, dias=30):
    today = date.today()
    return Matafuegos.objects.filter(
        company=company, fecha_proxima_carga__range=(today, today + timedelta(dias)),
    ).order_by('categoria', 'cliente__nombre')


def list_proximos_vencimientos_ph(company, dias=30):
    today = date.today()
    return Matafuegos.objects.filter(
        company=company, fecha_proxima_ph__range=(today, today + timedelta(dias)),
    ).order_by('categoria', 'cliente__nombre')


def matafuegos_de_cliente(cliente):
    return Matafuegos.objects.filter(cliente=cliente).order_by('numero')


def count_matafuegos(company):
    return Matafuegos.objects.filter(company=company).count()


def count_vencimiento_proximo(company, dias=30):
    today = date.today()
    horizon = today + timedelta(dias)
    return Matafuegos.objects.filter(company=company).filter(
        Q(fecha_proxima_carga__range=(today, horizon)) | Q(fecha_proxima_ph__range=(today, horizon))
    ).distinct().count()


def vencimiento_relevante(matafuego):
    """(tipo_vencimiento, fecha) del ciclo de vencimiento que corresponde
    mostrar/notificar para este matafuego: carga y PH son ciclos
    independientes (cada uno con su propia fecha_carga/fecha_ph), y acá se
    toma el más próximo/urgente de los dos para representar el vencimiento
    del matafuego con un solo estado. Devuelve (None, None) si no tiene
    ningún vencimiento cargado."""
    from matafuegos.models import NotificacionVencimiento

    carga = matafuego.fecha_proxima_carga
    ph = matafuego.fecha_proxima_ph
    if carga and ph:
        if carga <= ph:
            return NotificacionVencimiento.TIPO_CARGA, carga
        return NotificacionVencimiento.TIPO_PH, ph
    if carga:
        return NotificacionVencimiento.TIPO_CARGA, carga
    if ph:
        return NotificacionVencimiento.TIPO_PH, ph
    return None, None


def notificacion_vigente(matafuego):
    """Última NotificacionVencimiento (la más reciente) que corresponde al
    ciclo de vencimiento ACTUAL del matafuego (mismo tipo_vencimiento y
    misma fecha_vencimiento que devuelve vencimiento_relevante), o None si
    todavía no se notificó nada para este ciclo -- ya sea porque nunca se
    notificó, o porque una recarga/PH nueva cambió la fecha y dejó
    automáticamente afuera cualquier notificación de un ciclo anterior."""
    tipo_vencimiento, fecha_vencimiento = vencimiento_relevante(matafuego)
    if not fecha_vencimiento:
        return None
    return matafuego.notificaciones.filter(
        tipo_vencimiento=tipo_vencimiento, fecha_vencimiento=fecha_vencimiento,
    ).order_by('-created_at').first()


DIAS_PROXIMO_A_VENCER = 30

ESTADO_VENCIMIENTO_AL_DIA = 'al_dia'
ESTADO_VENCIMIENTO_PROXIMO = 'proximo'
ESTADO_VENCIMIENTO_VENCIDO = 'vencido'


def estado_vencimiento(fecha_vencimiento, dias=DIAS_PROXIMO_A_VENCER):
    """Al día / Próximo a vencer / Vencido para una fecha de vencimiento ya
    resuelta (ver vencimiento_relevante). None si no hay fecha."""
    if fecha_vencimiento is None:
        return None
    hoy = date.today()
    if fecha_vencimiento < hoy:
        return ESTADO_VENCIMIENTO_VENCIDO
    if fecha_vencimiento <= hoy + timedelta(days=dias):
        return ESTADO_VENCIMIENTO_PROXIMO
    return ESTADO_VENCIMIENTO_AL_DIA


def list_panel_vencimientos(company, q=None, tipo=None, estado=None, cliente=None):
    """Una fila por matafuego (con algún vencimiento cargado) para el panel
    interactivo de Vencimientos, con su ciclo relevante, el estado de ese
    vencimiento y el estado de notificación vigente para ese mismo ciclo.

    Devuelve TODAS las filas que matchean q/tipo/estado/cliente, sin
    recortar por el filtro de pestaña (Todos/Próximos/Vencidos/Sin
    notificar/Notificados) -- eso lo hace `aplicar_filtro_vencimientos` a
    continuación, aparte, para poder calcular los contadores de cada
    pestaña sobre la misma lista base sin repetir la consulta.

    `estado`: 'a' (Activo) | 'i' (Inactivo) | None/'' para no filtrar (ambos
    a la vez) -- mismo comportamiento que `list_matafuegos`, sin ningún
    default oculto acá; el default visible de "solo Activos" lo pone la
    vista al armar el desplegable, no esta función."""
    qs = Matafuegos.objects.filter(company=company).filter(
        Q(fecha_proxima_carga__isnull=False) | Q(fecha_proxima_ph__isnull=False)
    )
    if estado:
        qs = qs.filter(estado=estado)
    if tipo:
        qs = qs.filter(tipo_id=tipo)
    if cliente:
        qs = qs.filter(cliente_id=cliente)
    if q:
        qs = qs.filter(Q(numero__icontains=q) | Q(cliente__nombre__icontains=q) | Q(cliente__codigo__icontains=q) | Q(tipo__tipo__icontains=q))
    qs = qs.select_related('cliente', 'company', 'tipo').order_by('cliente__nombre', 'numero')

    filas = []
    for matafuego in qs:
        tipo_vencimiento, fecha_vencimiento = vencimiento_relevante(matafuego)
        if not fecha_vencimiento:
            continue
        notificacion = notificacion_vigente(matafuego)
        filas.append({
            'matafuego': matafuego,
            'tipo_vencimiento': tipo_vencimiento,
            'fecha_vencimiento': fecha_vencimiento,
            'estado_vencimiento': estado_vencimiento(fecha_vencimiento),
            'notificacion': notificacion,
            'estado_notificacion': notificacion.estado_envio if notificacion else None,
        })
    return filas


def aplicar_filtro_vencimientos(filas, filtro):
    """Recorta `filas` (la lista que devuelve list_panel_vencimientos) según
    la pestaña activa. 'sin_notificar' agrupa Sin notificar, Pendiente de
    confirmación y Error -- todo lo que todavía no tiene una notificación
    válida (NOTIFICADA) para el ciclo actual, que es exactamente lo que hay
    que seguir trabajando; el badge de cada fila igual distingue los cuatro
    estados, esto solo agrupa para el filtro."""
    from matafuegos.models import NotificacionVencimiento

    if filtro == 'proximos':
        return [f for f in filas if f['estado_vencimiento'] == ESTADO_VENCIMIENTO_PROXIMO]
    if filtro == 'vencidos':
        return [f for f in filas if f['estado_vencimiento'] == ESTADO_VENCIMIENTO_VENCIDO]
    if filtro == 'sin_notificar':
        return [f for f in filas if f['estado_notificacion'] != NotificacionVencimiento.ESTADO_NOTIFICADA]
    if filtro == 'notificados':
        return [f for f in filas if f['estado_notificacion'] == NotificacionVencimiento.ESTADO_NOTIFICADA]
    return filas


def contar_vencimientos_por_filtro(filas):
    """Contadores de cada pestaña (Todos/Próximos/Vencidos/Sin notificar/
    Notificados) sobre la misma lista base de filas -- independientes de
    cuál esté activa, para que los 5 números se vean siempre juntos."""
    from matafuegos.models import NotificacionVencimiento

    return {
        'todos': len(filas),
        'proximos': sum(1 for f in filas if f['estado_vencimiento'] == ESTADO_VENCIMIENTO_PROXIMO),
        'vencidos': sum(1 for f in filas if f['estado_vencimiento'] == ESTADO_VENCIMIENTO_VENCIDO),
        'sin_notificar': sum(1 for f in filas if f['estado_notificacion'] != NotificacionVencimiento.ESTADO_NOTIFICADA),
        'notificados': sum(1 for f in filas if f['estado_notificacion'] == NotificacionVencimiento.ESTADO_NOTIFICADA),
    }
