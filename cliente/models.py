from cffi.backend_ctypes import xrange
from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse
from django.core.validators import URLValidator

estados = [
        ('a', 'Activo'),
        ('i', 'Inactivo'),
    ]

class Cliente(models.Model):
    tipos = [
        ('p', 'Persona'),
        ('e', 'Empresa'),
    ]

    company = models.ForeignKey('empresas.Company', verbose_name='Compañía', on_delete=models.PROTECT, related_name='clientes')
    codigo = models.CharField("Codigo", max_length=50)
    cuit_cuil = models.CharField('CUIT/CUIL', max_length=11, null=True, blank=True,  help_text="Solo se deben ingresar numeros")
    nombre = models.CharField('Nombre/ Razón Social', max_length=80)
    contacto= models.CharField('Nombre contacto', max_length=80, null= True, blank=True)
    direccion = models.CharField('Dirección', max_length=80, null=True)
    telefono = models.CharField('Telefono', max_length=80, null=True)
    email = models.EmailField('Email', blank=True, max_length=264, null=True)
    web = models.URLField('Web', blank=True, max_length=200, null=True)
    tipo = models.CharField('Tipo', max_length=80, choices=tipos, default= 'p')
    estado = models.CharField('Estado', max_length=80, choices=estados, default= 'a')

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['company', 'codigo'], name='cliente_company_codigo_unique'),
        ]

    #def get_absolute_url(self):
        #return reverse('cliente-detalle', args=[str(self.id)])

    def __str__(self):
        return str(self.nombre+" - "+str(self.codigo))

    def validar_cuit(self, cuit):
        # validaciones minimas
        if cuit is not None:
            if len(cuit) != 11:
                return False

            base = [5, 4, 3, 2, 7, 6, 5, 4, 3, 2]

            # calculo el digito verificador:
            aux = 0
            for i in xrange(10):
                aux += int(cuit[i]) * base[i]

            aux = 11 - (aux - (int(aux / 11) * 11))

            if aux == 11:
                aux = 0
            if aux == 10:
                aux = 9

            return aux == int(cuit[10])
        return True
    def clean(self):
        cleaned_data = super().clean()
        if not self.validar_cuit(self.cuit_cuil):
            raise ValidationError('El cuit_cuil del cliente es invalido')

        #validate = URLValidator(verify_exists=True)
        #try:
        #    validate(self.web)
        #except ValidationError as e:
        #    raise ValidationError('La direccion web ingresada no es valida')
        return cleaned_data

    def save(self, *args, **kwargs):
        #if self.codigo == -1:
            #self.codigo = int(str(Cliente.objects.raw('SELECT codigo FROM public.cliente_cliente ORDER BY codigo ASC')[-1]).split()[-1])+1
        super(Cliente, self).save(*args, **kwargs)

