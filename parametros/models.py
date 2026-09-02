from django.core.exceptions import ValidationError
from django.db import models

# Create your models here.
class Parametros(models.Model):
    veh_inicio = models.IntegerField('VEH inicio', default=0)
    veh_fin = models.IntegerField('VEH fin', default=0)
    veh_prefijo = models.CharField('VEH prefijo', max_length=5, default="")
    veh_actual = models.IntegerField('VEH actual', default=0)
    dom_inicio = models.IntegerField('DOM inicio', default=0)
    dom_fin = models.IntegerField('DOM fin', default=0)
    dom_prefijo = models.CharField('DOM prefijo', max_length=5, default="")
    dom_actual = models.IntegerField('DOM actual', default=0)
    email = models.EmailField('Email', blank=True, max_length=264, null=True)
    password = models.CharField('Contraseña',blank=True, max_length=20, null=True)

    def clean(self):
        cleaned_data = super().clean()
        if self.veh_inicio<0:
            raise ValidationError('El VEH inicio debe ser mayor o igual a 0')
        if self.veh_fin<0:
            raise ValidationError('El VEH fin debe ser mayor o igual a 0')
        if self.veh_actual<0:
            raise ValidationError('El VEH actual debe ser mayor o igual a 0')
        if self.veh_actual<self.veh_inicio:
            raise ValidationError('El VEH actual debe ser mayor o igual al VEH inicio')
        if self.veh_actual>self.veh_fin:
            raise ValidationError('El VEH actual debe ser menor o igual al VEH fin')
        if self.dom_inicio<0:
            raise ValidationError('El DOM inicio debe ser mayor o igual a 0')
        if self.dom_fin<0:
            raise ValidationError('El DOM fin debe ser mayor o igual a 0')
        if self.dom_actual<0:
            raise ValidationError('El DOM actual debe ser mayor o igual a 0')
        if self.dom_actual<self.dom_inicio:
            raise ValidationError('El DOM actual debe ser mayor o igual al DOM inicio')
        if self.dom_actual>self.dom_fin:
            raise ValidationError('El DOM actual debe ser menor o igual al DOM fin')

    class Meta:
        verbose_name_plural = "Parametros"
