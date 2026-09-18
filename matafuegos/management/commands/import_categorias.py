from django.core.management.base import BaseCommand
from django.db import transaction

from matafuegos.models.categoria import CategoriaMatafuegos

CATEGORIAS = [
    (1, 'A'),
    (2, 'BC'),
    (3, 'ABC'),
    (4, 'AFFF'),
    (5, 'HCFC'),
    (6, 'K'),
]


class Command(BaseCommand):
    help = 'Importa las categorias de matafuegos'

    @transaction.atomic
    def handle(self, *args, **options):
        creadas = 0
        actualizadas = 0
        for id_, nombre in CATEGORIAS:
            _, created = CategoriaMatafuegos.objects.update_or_create(
                id=id_,
                defaults={'nombre': nombre},
            )
            if created:
                creadas += 1
            else:
                actualizadas += 1

        self.stdout.write(self.style.SUCCESS(
            f'Categorias importadas: {creadas} creadas, {actualizadas} actualizadas.'
        ))
