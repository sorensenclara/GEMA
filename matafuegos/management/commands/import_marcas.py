from django.core.management.base import BaseCommand
from django.db import transaction

from matafuegos.models.marca import MarcaMatafuegos

MARCAS = [
    (1, 'Inflex'),
    (2, 'Tible'),
    (3, 'Sentry'),
    (4, 'Drago '),
    (5, 'Yanes'),
    (6, 'Fedesa S.A.'),
    (7, 'Georgia'),
    (8, 'Horizonte'),
    (9, 'Fistoray'),
    (10, 'Previsol'),
    (11, 'Fadesa Mafu'),
    (12, 'Mathil'),
    (13, 'Melisam'),
    (14, 'Norbco'),
    (15, 'Motorcraf'),
    (16, 'Premier'),
    (17, 'RESIL'),
    (18, 'S/M'),
    (19, 'Tanzi'),
    (20, 'Fuegomat'),
    (21, 'MAT Luda'),
    (22, 'Yukon'),
]


class Command(BaseCommand):
    help = 'Importa las marcas de matafuegos'

    @transaction.atomic
    def handle(self, *args, **options):
        creadas = 0
        actualizadas = 0
        for id_, nombre in MARCAS:
            _, created = MarcaMatafuegos.objects.update_or_create(
                id=id_,
                defaults={'nombre': nombre},
            )
            if created:
                creadas += 1
            else:
                actualizadas += 1

        self.stdout.write(self.style.SUCCESS(
            f'Marcas importadas: {creadas} creadas, {actualizadas} actualizadas.'
        ))
