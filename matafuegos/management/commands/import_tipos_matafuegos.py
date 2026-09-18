from django.core.management.base import BaseCommand
from django.db import transaction

from matafuegos.models.tipo import TipoMatafuegos

# (id, categoria_id, tipo, volumen, peso, vencimiento_carga, vencimiento_ph)
TIPOS = [
    (1, 1, 'A 100', 100, 0, None, None),
    (2, 1, 'A 25', 25, 0, None, None),
    (3, 2, 'BC 2', 2, 0, None, None),
    (4, 3, 'ABC 2.5', 2.5, 0, None, None),
    (5, 3, 'ABC 100', 100, 0, None, None),
    (6, 3, 'ABC 10', 10, 0, None, None),
    (7, 3, 'ABC 25', 25, 0, None, None),
    (8, 3, 'ABC 75', 75, 0, None, None),
    (9, 2, 'BC 10', 10, 0, None, None),
    (10, 2, 'BC 5', 5, 0, None, None),
    (11, 2, 'BC 3.5', 3.5, 0, None, None),
    (12, 2, 'BC 7', 7, 0, None, None),
    (13, 4, 'AFFF 10', 10, 0, None, None),
    (14, 1, 'A 50', 50, 0, None, None),
    (15, 1, 'A 75', 75, 0, None, None),
    (16, 2, 'BC 25', 25, 0, None, None),
    (17, 3, 'ABC 1', 1, 0, None, None),
    (18, 5, 'HCFC 5', 5, 0, None, None),
    (19, 3, 'ABCK 6', 6, 0, None, None),
    (20, 4, 'AFFF 75', 75, 0, None, None),
    (21, 3, 'ABC 5', 5, 0, None, None),
    (22, 5, 'HCFC 10', 10, 0, None, None),
    (23, 3, 'ABC 70', 70, 0, None, None),
    (24, 3, 'ABC 50', 50, 0, None, None),
    (25, 4, 'AFFF 100', 100, 0, None, None),
    (26, 3, 'POLVO BC X 25 KG', 0, 0, None, None),
    (27, 1, 'A 10', 10, 0, None, None),
    (28, 6, 'ABCK 10', 10, 0, None, None),
    (29, 2, 'BC 2.5', 2.50, 0, None, None),
    (30, 3, 'ABC 4', 4, 0, None, None),
    (31, 5, 'HCFC 1', 1, 0, None, None),
    (32, 4, 'AFFF 5', 5, 0, None, None),
    (33, 6, 'K 10', 10, 0, None, None),
    (34, 5, 'HCFC 2.5', 2.5, 0, None, None),
    (35, 2, 'BC 20', 20, 0, None, None),
    (36, 3, 'ABC 6', 6, 0, None, None),
    (37, 2, 'BC 3', 3, 0, None, None),
    (38, 4, 'AFFF 50', 50, 0, None, None),
    (39, 4, 'ARAFFF 25', 25, 0, None, None),
    (40, 4, 'ARAFFF X 25 LTS', 0, 0, None, None),
    (41, 6, 'ABCK 2.5', 2, 2.5, None, None),
    (42, 6, 'AK 6', 6, 0, None, None),
    (43, 3, 'ABC 2', 2, 0, None, None),
]


class Command(BaseCommand):
    help = 'Importa los tipos de matafuegos'

    @transaction.atomic
    def handle(self, *args, **options):
        creados = 0
        actualizados = 0
        for id_, categoria_id, tipo, volumen, peso, venc_carga, venc_ph in TIPOS:
            _, created = TipoMatafuegos.objects.update_or_create(
                id=id_,
                defaults={
                    'categoria_id': categoria_id,
                    'tipo': tipo,
                    'volumen': volumen,
                    'peso': peso,
                    'vencimiento_carga': venc_carga,
                    'vencimiento_ph': venc_ph,
                },
            )
            if created:
                creados += 1
            else:
                actualizados += 1

        self.stdout.write(self.style.SUCCESS(
            f'Tipos de matafuegos importados: {creados} creados, {actualizados} actualizados.'
        ))
