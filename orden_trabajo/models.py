from datetime import date
from django.contrib import admin
from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse
from cliente.models import Cliente
from matafuegos.models import Matafuegos
from urllib3.util import request


class Tarea(models.Model):
    company = models.ForeignKey('empresas.Company', verbose_name='Compañía', on_delete=models.PROTECT, related_name='tareas')
    nombre = models.CharField('Nombre', max_length=120)
    precio = models.FloatField("Precio", default=0)
    es_recarga = models.BooleanField(
        'Es tarea de recarga', default=False,
        help_text='Marca esta tarea como recarga: una orden solo puede emitir su oblea DPS al finalizarse si incluye alguna tarea marcada así.',
    )

    #def get_absolute_url(self):
        #return reverse('tarea-detalle', args=[str(self.id)])

    def clean(self):
        cleaned_data = super().clean()
        if self.precio<0:
            raise ValidationError('El precio debe ser mayor a 0')
        return cleaned_data

    def __str__(self):
        return str(self.nombre+" - $"+str(self.precio))


estados = [
    ('p', 'Pendiente'),
    ('ep', 'En proceso'),
    ('f', 'Finalizada'),
    ('i', 'Impresa'),
    ('fac', 'Facturada' ),
    ('c', 'Cancelada'),
]

class Ordenes_de_trabajo(models.Model):

    company = models.ForeignKey('empresas.Company', verbose_name='Compañía', on_delete=models.PROTECT, related_name='ordenes_de_trabajo')
    fecha_creacion = models.DateField("Fecha de creacion de orden", default=date.today)
    fecha_inicio = models.DateField("Fecha de inicio", blank=True, null=True,default=date.today)
    fecha_entrega= models.DateField("Entrega estimada", default=date.today)
    fecha_cierre= models.DateField("Fecha de cierre", blank=True, null=True)
    cliente = models.ForeignKey(Cliente,verbose_name='Cliente', on_delete=models.CASCADE, related_name='ordenes_de_trabajo')
    matafuegos = models.ForeignKey(Matafuegos, verbose_name='Matafuegos', on_delete=models.CASCADE, related_name='ordenes_de_trabajo')
    estado = models.CharField('Estado', max_length=80, choices=estados, default= 'ep')
    monto_total = models.FloatField('Monto', default=0)
    notas = models.CharField('Notas', max_length=80, blank=True)
    usuario= models.CharField('Usuario responsable', max_length=30, default='')


    def calcular_monto(self):
        monto=0
        i=0
        for p in TareaOrden.objects.filter(orden=self).values_list('tarea'):
            if TareaOrden.objects.filter(orden=self).values_list('precioAj')[i][0] == 0.0:
                monto+= Tarea.objects.filter(id=p[0]).values_list('precio')[0][0]
            else:
                monto+= TareaOrden.objects.filter(orden=self).values_list('precioAj')[i][0]
            i+=1
        return monto


    """
    @admin.display(boolean=True)
    def estados(self):
        if self.estado in ['f', 'c']:
            return False
        return True
    """


    def save(self, *args, **kwargs ):
        self.monto_total = self.calcular_monto()
        super(Ordenes_de_trabajo,self).save(*args, **kwargs)

    #def get_absolute_url(self):
        #return reverse('ordenes_de_trabajo-detalle', args=[str(self.id)])

    def __str__(self):
        return str(self.id)

    class Meta:
      verbose_name_plural = "Ordenes de trabajo"

class TareaOrden(models.Model):
    tarea = models.ForeignKey(Tarea, verbose_name='Tarea', on_delete=models.CASCADE)
    orden = models.ForeignKey(Ordenes_de_trabajo,verbose_name='Orden', on_delete=models.CASCADE)
    precioAj = models.FloatField('Precio ajustable', default=0)
    cant_cargada = models.FloatField('Cantidad cargada', default=0)

    def save(self, *args, **kwargs):
        super(TareaOrden, self).save(*args, **kwargs)
        self.orden.save()

    def clean(self):
        cleaned_data = super().clean()
        if self.precioAj<0:
            raise ValidationError('El precio debe ser mayor o igual a 0')
        if self.cant_cargada<0:
            raise ValidationError('La cantidad debe ser mayor o igual a 0')
        return cleaned_data

    #def get_absolute_url(self):
        #return reverse('tarea_orden-detalle', args=[str(self.id)])

    class Meta:
        verbose_name_plural = "Tarea - Orden de trabajo"

    def __str__(self):
        return str(self.id)

