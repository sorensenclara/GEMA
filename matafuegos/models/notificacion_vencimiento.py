from django.db import models

from core.models import AuditModel


class NotificacionVencimiento(AuditModel):
    """
    Registro de un intento de notificación de vencimiento (carga o PH) de un
    matafuego a su cliente. Cada instancia está atada a un ciclo de
    vencimiento específico (tipo_vencimiento + fecha_vencimiento): una
    recarga o PH nueva cambia esa fecha en el matafuego y automáticamente
    deja de existir una notificación vigente para el ciclo nuevo, sin
    heredar el estado de una notificación anterior.

    El envío nunca es automático: se resuelve en dos pasos manuales.
    1) Al abrir el enlace `wa.me` (botón "Enviar WhatsApp") se crea el
       registro en PENDIENTE.
    2) Al volver de WhatsApp, el usuario cierra el intento con
       "Marcar como enviado" (NOTIFICADA) o "Hubo un error" (ERROR).
    Un registro en NOTIFICADA o en ERROR nunca se reabre ni se sobrescribe:
    un reintento posterior siempre crea un registro nuevo, preservando el
    historial completo (incluida la tabla histórica automática de
    django-simple-history, heredada de AuditModel).
    """

    TIPO_CARGA = 'carga'
    TIPO_PH = 'ph'

    TIPOS_VENCIMIENTO = [
        (TIPO_CARGA, 'Próxima carga'),
        (TIPO_PH, 'Próxima PH'),
    ]

    MEDIO_WHATSAPP = 'whatsapp'

    MEDIOS = [
        (MEDIO_WHATSAPP, 'WhatsApp'),
    ]

    ESTADO_PENDIENTE = 'pendiente'
    ESTADO_NOTIFICADA = 'notificada'
    ESTADO_ERROR = 'error'

    ESTADOS_ENVIO = [
        (ESTADO_PENDIENTE, 'Pendiente de confirmación'),
        (ESTADO_NOTIFICADA, 'Notificada'),
        (ESTADO_ERROR, 'Error'),
    ]

    matafuego = models.ForeignKey(
        'matafuegos.Matafuegos',
        on_delete=models.PROTECT,
        related_name='notificaciones',
        verbose_name='Matafuego',
    )

    tipo_vencimiento = models.CharField(
        'Tipo de vencimiento',
        max_length=20,
        choices=TIPOS_VENCIMIENTO,
    )

    fecha_vencimiento = models.DateField(
        'Vencimiento informado',
    )

    medio = models.CharField(
        'Medio',
        max_length=20,
        choices=MEDIOS,
        default=MEDIO_WHATSAPP,
    )

    numero_destino = models.CharField(
        'Número de destino',
        max_length=30,
    )

    mensaje = models.TextField(
        'Mensaje',
        blank=True,
    )

    estado_envio = models.CharField(
        'Estado del envío',
        max_length=20,
        choices=ESTADOS_ENVIO,
        default=ESTADO_PENDIENTE,
    )

    external_message_id = models.CharField(
        'ID externo del mensaje',
        max_length=255,
        blank=True,
        null=True,
    )

    observacion = models.TextField(
        'Observación',
        blank=True,
    )

    class Meta:
        verbose_name = 'Notificación de vencimiento'
        verbose_name_plural = 'Notificaciones de vencimiento'
        ordering = ['-created_at']
        indexes = [
            models.Index(
                fields=['matafuego', 'tipo_vencimiento', 'fecha_vencimiento', 'estado_envio'],
                name='matafuegos_notif_ciclo_idx',
            ),
        ]

    def __str__(self):
        return (
            f'{self.matafuego} - '
            f'{self.get_tipo_vencimiento_display()} - '
            f'{self.fecha_vencimiento} - '
            f'{self.get_estado_envio_display()}'
        )
