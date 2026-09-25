from django.core.exceptions import ValidationError
from django.db import models

from core.models import AuditModel
from core.utils import TelefonoInvalidoException, normalizar_telefono_ar

ESTADOS = [
    ('a', 'Activo'),
    ('i', 'Inactivo'),
]

GEO_STATUS_CHOICES = [
    ('georreferenciado', 'Georreferenciado'),
    ('manual_legado', 'Manual (legado)'),
    ('manual_no_encontrado', 'Manual (no encontrado)'),
]


class Cliente(AuditModel):
    TIPOS = [
        ('p', 'Persona'),
        ('e', 'Empresa'),
    ]

    company = models.ForeignKey('empresas.Company', verbose_name='Compañía', on_delete=models.PROTECT, related_name='clientes')
    codigo = models.CharField("Codigo", max_length=50)
    cuit_cuil = models.CharField('CUIT/CUIL', max_length=11, null=True, blank=True, help_text="Solo se deben ingresar numeros")
    nombre = models.CharField('Nombre/ Razón Social', max_length=80)
    contacto = models.CharField('Nombre contacto', max_length=80, null=True, blank=True)
    direccion = models.CharField('Dirección', max_length=255, null=True)
    localidad = models.CharField('Localidad', max_length=120, null=True, blank=True)
    provincia = models.CharField('Provincia', max_length=120, null=True, blank=True)
    codigo_postal = models.CharField('Código postal', max_length=20, null=True, blank=True)
    pais = models.CharField('País', max_length=80, null=True, blank=True)
    # osm_type:osm_id de Nominatim (ver core/services/geocoding.py) -- NO es
    # el place_id de Nominatim, que su propia documentación marca como
    # interno y no estable entre instalaciones/actualizaciones.
    geo_referencia_externa = models.CharField('Referencia externa de ubicación', max_length=50, null=True, blank=True)
    geo_provider = models.CharField('Proveedor de geocodificación', max_length=30, null=True, blank=True)
    geo_status = models.CharField('Estado de georreferenciación', max_length=25, choices=GEO_STATUS_CHOICES, null=True, blank=True)
    telefono = models.CharField('Telefono', max_length=80, null=True)
    email = models.EmailField('Email', blank=True, max_length=264, null=True)
    web = models.URLField('Web', blank=True, max_length=200, null=True)
    tipo = models.CharField('Tipo', max_length=80, choices=TIPOS, default='p')
    estado = models.CharField('Estado', max_length=80, choices=ESTADOS, default='a')

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['company', 'codigo'], name='cliente_company_codigo_unique'),
        ]

    def __str__(self):
        return f'{self.nombre} - {self.codigo}'

    def validar_cuit(self, cuit):
        if cuit is None:
            return True
        if len(cuit) != 11:
            return False

        base = [5, 4, 3, 2, 7, 6, 5, 4, 3, 2]
        aux = sum(int(cuit[i]) * base[i] for i in range(10))
        aux = 11 - (aux - (int(aux / 11) * 11))
        if aux == 11:
            aux = 0
        if aux == 10:
            aux = 9
        return aux == int(cuit[10])

    def clean(self):
        cleaned_data = super().clean()
        if not self.validar_cuit(self.cuit_cuil):
            raise ValidationError('El cuit_cuil del cliente es invalido')
        if self.telefono:
            try:
                self.telefono = normalizar_telefono_ar(self.telefono)
            except TelefonoInvalidoException as exc:
                raise ValidationError({'telefono': str(exc)})
        return cleaned_data
