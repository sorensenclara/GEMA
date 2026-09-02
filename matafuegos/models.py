from datetime import date
import datetime

from django.core.exceptions import ValidationError
from django.db import models
from django.http import HttpResponse

# Create your models here.
from cliente.models import Cliente
#from rest_framework.exceptions import ValidationError


class CategoriaMatafuegos(models.Model):
    nombre = models.CharField('Nombre', max_length=20)

    def __str__(self):
        return self.nombre
    class Meta:
        verbose_name_plural = "Categoria Matafuegos"

class TipoMatafuegos(models.Model):
    tipo = models.CharField('Tipo', max_length=20)
    categoria = models.ForeignKey(CategoriaMatafuegos, verbose_name='Categoria', on_delete=models.CASCADE, null=True, blank=True)
    vencimiento_carga = models.IntegerField('Vencimiento de carga', help_text="Cantidad de dias", null=True, blank=True)
    vencimiento_ph = models.IntegerField('Vencimiento de PH', help_text="Cantidad de dias", null=True, blank=True)
    volumen = models.FloatField('Volumen', null=True, blank=True)
    peso = models.FloatField('Peso', null=True, blank=True)

    def clean(self):
        cleaned_data = super().clean()
        if self.vencimiento_carga:
            if self.vencimiento_carga<0:
                raise ValidationError('El numero de dias de vencimeinto de carga debe ser mayor a 0')
        if self.vencimiento_ph:
            if self.vencimiento_ph<0:
                raise ValidationError('El numero de dias de vencimeinto de ph debe ser mayor a 0')
        if self.volumen:
            if self.volumen<0:
                raise ValidationError('El volumen debe ser mayor a 0')
        if self.peso:
            if self.peso<0:
                raise ValidationError('El peso debe ser mayor a 0')
        return cleaned_data

    def __str__(self):
        return self.tipo
    class Meta:
        verbose_name_plural = "Tipo Matafuegos"

class MarcaMatafuegos(models.Model):
    nombre = models.CharField('Nombre', max_length=15)

    def __str__(self):
        return self.nombre
    class Meta:
        verbose_name_plural = "Marca Matafuegos"

class Matafuegos(models.Model):
    company = models.ForeignKey('empresas.Company', verbose_name='Compañía', on_delete=models.PROTECT, related_name='matafuegos')
    numero = models.IntegerField('Numero')
    numeroInterno= models.IntegerField('Numero interno',blank=True, null= True)
    cliente = models.ForeignKey(Cliente, verbose_name='Cliente', on_delete=models.RESTRICT, related_name='matafuegos')
    patente = models.CharField('Patente', max_length=19, blank=True, null= True)
    direccion = models.CharField('Direccion', max_length=30, null=True, blank=True)
    localizacion = models.CharField('Localizacion', max_length=100, blank=True, null= True)
    numero_localizacion = models.IntegerField('Numero de localizacion', null=True, blank=True)
    marca = models.ForeignKey(MarcaMatafuegos, verbose_name='Marca', on_delete=models.CASCADE, null=True)
    tipo = models.ForeignKey(TipoMatafuegos, verbose_name='Tipo', on_delete=models.CASCADE)
    cat = [('v', 'Vehicular'),('d', 'Domiciliario'),('ma', 'Maquinaria Agricola')]
    categoria = models.CharField('Categoria', max_length=20, choices=cat)
    fecha_fabricacion = models.DateField('Fecha de fabricacion', null=True)
    fecha_carga = models.DateField('Fecha de carga',default=datetime.date.today, null= True)
    fecha_ph = models.DateField('Fecha de PH',default=datetime.date.today, null=True)
    numero_dps = models.CharField('Numero de DPS', null=True, blank=True, max_length=50)
    fecha_proxima_carga = models.DateField('Fecha de proxima carga',null=True, blank=True)
    fecha_proxima_ph = models.DateField('Fecha de proxima PH',null=True, blank=True)
    vencido = models.BooleanField('Vencido', default= False)

    def clean(self):
        cleaned_data = super().clean()
        if self.numero<0:
            raise ValidationError('El numero del matafuego debe ser mayor a 0')
        if self.numeroInterno:
            if int(self.numeroInterno)<0:
                raise ValidationError('El numero interno debe ser mayor a 0')
        if not self.patente and self.categoria == 'v':
            raise ValidationError('Debe especificar la patente del vehiculo')
        if self.fecha_fabricacion:
            if self.fecha_fabricacion > date.today():
                raise ValidationError('La fecha de fabicacion tiene que ser anterior o igual a la fecha de hoy')
        if self.fecha_carga:
            if self.fecha_carga > date.today():
                raise ValidationError('La fecha de carga tiene que ser anterior o igual a la fecha de hoy')
        if self.fecha_ph:
            if self.fecha_ph > date.today():
                raise ValidationError('La fecha de ph tiene que ser anterior o igual a la fecha de hoy')
        if self.fecha_carga and self.fecha_fabricacion:
            if self.fecha_carga < self.fecha_fabricacion:
                raise ValidationError('La fecha de carga tiene que ser anterior o igual a la fecha de fabricacion')
        if self.fecha_ph and self.fecha_fabricacion:
            if self.fecha_ph < self.fecha_fabricacion:
                raise ValidationError('La fecha de ph tiene que ser anterior o igual a la fecha de fabricacion')

        return cleaned_data

    def calcularFecha(self, fecha, dias):
        return fecha + datetime.timedelta(days=dias)

    def save(self, *args, **kwargs):
        if self.categoria == 'ma':
            self.patente='Maquina agricola'
        if self.tipo.vencimiento_carga and self.fecha_carga:
            self.fecha_proxima_carga = self.calcularFecha(self.fecha_carga, self.tipo.vencimiento_carga)
        if self.tipo.vencimiento_ph and self.fecha_ph:
            self.fecha_proxima_ph = self.calcularFecha(self.fecha_ph, self.tipo.vencimiento_ph)
        super(Matafuegos, self).save(*args, **kwargs)

    class Meta:
        verbose_name_plural = "Matafuegos"

    def __str__(self):
        return str(str(self.numero) + "-" + str(self.tipo))



