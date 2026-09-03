from django.core.exceptions import ValidationError
from django.db import models

from core.models import AuditModel


class Tarea(AuditModel):
    company = models.ForeignKey('empresas.Company', verbose_name='Compañía', on_delete=models.PROTECT, related_name='tareas')
    nombre = models.CharField('Nombre', max_length=120)
    precio = models.FloatField("Precio", default=0)
    es_recarga = models.BooleanField(
        'Es tarea de recarga', default=False,
        help_text='Marca esta tarea como recarga: una orden solo puede emitir su oblea DPS al finalizarse si incluye alguna tarea marcada así.',
    )

    def clean(self):
        cleaned_data = super().clean()
        if self.precio < 0:
            raise ValidationError('El precio debe ser mayor a 0')
        return cleaned_data

    def __str__(self):
        return f'{self.nombre} - ${self.precio}'
