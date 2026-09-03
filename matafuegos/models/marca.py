from django.db import models


class MarcaMatafuegos(models.Model):
    nombre = models.CharField('Nombre', max_length=15)

    class Meta:
        verbose_name_plural = "Marca Matafuegos"

    def __str__(self):
        return self.nombre
