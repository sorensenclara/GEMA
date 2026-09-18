from django.db import models

from core.models import AuditModel


class Company(AuditModel):
    nombre = models.CharField('Nombre', max_length=200)
    logo = models.ImageField('Logo', upload_to='company_logos/', null=True, blank=True)
    is_active = models.BooleanField('Activa', default=True)
    numero_recargador = models.CharField('Número de recargador', max_length=10, blank=True, default='')

    # Numeración DPS
    veh_inicio = models.IntegerField('VEH inicio', default=0)
    veh_fin = models.IntegerField('VEH fin', default=0)
    veh_prefijo = models.CharField('VEH prefijo', max_length=5, default="")
    veh_actual = models.IntegerField('VEH actual', default=0)
    dom_inicio = models.IntegerField('DOM inicio', default=0)
    dom_fin = models.IntegerField('DOM fin', default=0)
    dom_prefijo = models.CharField('DOM prefijo', max_length=5, default="")
    dom_actual = models.IntegerField('DOM actual', default=0)

    # SMTP para el envío de informes a clientes
    smtp_email = models.EmailField('Email', blank=True, null=True, max_length=264)
    smtp_password = models.CharField('Contraseña', blank=True, null=True, max_length=20)

    class Meta:
        verbose_name = 'Compañía'
        verbose_name_plural = 'Compañías'

    def __str__(self):
        return self.nombre
