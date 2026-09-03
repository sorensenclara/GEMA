from django.core.exceptions import ValidationError
from django.db import models

from matafuegos.models.categoria import CategoriaMatafuegos


class TipoMatafuegos(models.Model):
    tipo = models.CharField('Tipo', max_length=20)
    categoria = models.ForeignKey(CategoriaMatafuegos, verbose_name='Categoria', on_delete=models.CASCADE, null=True, blank=True)
    vencimiento_carga = models.IntegerField('Vencimiento de carga', help_text="Cantidad de dias", null=True, blank=True)
    vencimiento_ph = models.IntegerField('Vencimiento de PH', help_text="Cantidad de dias", null=True, blank=True)
    volumen = models.FloatField('Volumen', null=True, blank=True)
    peso = models.FloatField('Peso', null=True, blank=True)

    class Meta:
        verbose_name_plural = "Tipo Matafuegos"

    def __str__(self):
        return self.tipo

    def clean(self):
        cleaned_data = super().clean()
        if self.vencimiento_carga and self.vencimiento_carga < 0:
            raise ValidationError('El numero de dias de vencimeinto de carga debe ser mayor a 0')
        if self.vencimiento_ph and self.vencimiento_ph < 0:
            raise ValidationError('El numero de dias de vencimeinto de ph debe ser mayor a 0')
        if self.volumen and self.volumen < 0:
            raise ValidationError('El volumen debe ser mayor a 0')
        if self.peso and self.peso < 0:
            raise ValidationError('El peso debe ser mayor a 0')
        return cleaned_data
