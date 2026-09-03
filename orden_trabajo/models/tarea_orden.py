from django.core.exceptions import ValidationError
from django.db import models

from core.models import AuditModel
from orden_trabajo.models.orden import Ordenes_de_trabajo
from orden_trabajo.models.tarea import Tarea


class TareaOrden(AuditModel):
    tarea = models.ForeignKey(Tarea, verbose_name='Tarea', on_delete=models.CASCADE)
    orden = models.ForeignKey(Ordenes_de_trabajo, verbose_name='Orden', on_delete=models.CASCADE)
    precioAj = models.FloatField('Precio ajustable', default=0)
    cant_cargada = models.FloatField('Cantidad cargada', default=0)

    class Meta:
        verbose_name_plural = "Tarea - Orden de trabajo"

    def __str__(self):
        return str(self.id)

    def clean(self):
        cleaned_data = super().clean()
        if self.precioAj < 0:
            raise ValidationError('El precio debe ser mayor o igual a 0')
        if self.cant_cargada < 0:
            raise ValidationError('La cantidad debe ser mayor o igual a 0')
        return cleaned_data
