from django.db import models


class CategoriaMatafuegos(models.Model):
    nombre = models.CharField('Nombre', max_length=20)

    class Meta:
        verbose_name_plural = "Categoria Matafuegos"

    def __str__(self):
        return self.nombre
