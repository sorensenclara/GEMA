from datetime import date

from django.db import models

from cliente.models import Cliente
from core.models import AuditModel
from matafuegos.models import Matafuegos

ESTADOS = [
    ('p', 'Pendiente'),
    ('ep', 'En proceso'),
    ('f', 'Finalizada'),
    ('i', 'Impresa'),
    ('fac', 'Facturada'),
    ('c', 'Cancelada'),
]


class Ordenes_de_trabajo(AuditModel):
    company = models.ForeignKey('empresas.Company', verbose_name='Compañía', on_delete=models.PROTECT, related_name='ordenes_de_trabajo')
    fecha_creacion = models.DateField("Fecha de creacion de orden", default=date.today)
    fecha_inicio = models.DateField("Fecha de inicio", blank=True, null=True, default=date.today)
    fecha_entrega = models.DateField("Entrega estimada", default=date.today)
    fecha_cierre = models.DateField("Fecha de cierre", blank=True, null=True)
    cliente = models.ForeignKey(Cliente, verbose_name='Cliente', on_delete=models.CASCADE, related_name='ordenes_de_trabajo')
    matafuegos = models.ForeignKey(Matafuegos, verbose_name='Matafuegos', on_delete=models.CASCADE, related_name='ordenes_de_trabajo')
    estado = models.CharField('Estado', max_length=80, choices=ESTADOS, default='ep')
    numero_dps = models.CharField(
        'Numero de DPS', max_length=50, blank=True, null=True,
        help_text='Numero de DPS asignado al emitir la oblea, si la orden incluyo una tarea de recarga.',
    )
    monto_total = models.FloatField('Monto', default=0)
    notas = models.CharField('Notas', max_length=80, blank=True)
    usuario = models.CharField('Usuario responsable', max_length=30, default='')

    class Meta:
        verbose_name_plural = "Ordenes de trabajo"

    def __str__(self):
        return str(self.id)
