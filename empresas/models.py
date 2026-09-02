from django.db import models, transaction


class Company(models.Model):
    nombre = models.CharField('Nombre', max_length=200)
    logo = models.ImageField('Logo', upload_to='company_logos/', null=True, blank=True)
    is_active = models.BooleanField('Activa', default=True)
    fecha_creacion = models.DateTimeField('Fecha de creación', auto_now_add=True)

    # Numeración DPS (migrado desde parametros.Parametros)
    veh_inicio = models.IntegerField('VEH inicio', default=0)
    veh_fin = models.IntegerField('VEH fin', default=0)
    veh_prefijo = models.CharField('VEH prefijo', max_length=5, default="")
    veh_actual = models.IntegerField('VEH actual', default=0)
    dom_inicio = models.IntegerField('DOM inicio', default=0)
    dom_fin = models.IntegerField('DOM fin', default=0)
    dom_prefijo = models.CharField('DOM prefijo', max_length=5, default="")
    dom_actual = models.IntegerField('DOM actual', default=0)

    # SMTP para el envío de informes a clientes (migrado desde parametros.Parametros)
    smtp_email = models.EmailField('Email', blank=True, null=True, max_length=264)
    smtp_password = models.CharField('Contraseña', blank=True, null=True, max_length=20)

    class Meta:
        verbose_name = 'Compañía'
        verbose_name_plural = 'Compañías'

    def __str__(self):
        return self.nombre

    def incrementar_dps(self, serie, paso=2):
        """Asigna atómicamente el próximo número de DPS de la serie ('veh' u 'dom')
        y devuelve el valor ya formateado con su prefijo."""
        assert serie in ('veh', 'dom')
        campo_actual = f'{serie}_actual'
        campo_prefijo = f'{serie}_prefijo'
        with transaction.atomic():
            company = Company.objects.select_for_update().get(pk=self.pk)
            valor_impreso = f"{getattr(company, campo_prefijo)}{getattr(company, campo_actual)}"
            Company.objects.filter(pk=self.pk).update(
                **{campo_actual: models.F(campo_actual) + paso}
            )
        self.refresh_from_db(fields=[campo_actual])
        return valor_impreso
