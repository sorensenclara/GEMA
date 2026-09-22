from django.core.management.base import BaseCommand
from django.db import transaction

from cliente.models import Cliente
from core.utils import TelefonoInvalidoException, normalizar_telefono_ar


class Command(BaseCommand):
    help = (
        'Normaliza Cliente.telefono a formato internacional listo para WhatsApp '
        '(54 9 + 10 digitos). Por defecto solo informa los cambios que haria '
        '(dry-run); pasar --apply para guardarlos.'
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--apply', action='store_true',
            help='Guarda los telefonos normalizados. Sin esta bandera solo se informa (dry-run).',
        )

    def handle(self, *args, **options):
        aplicar = options['apply']
        clientes = (
            Cliente.objects
            .exclude(telefono__isnull=True)
            .exclude(telefono__exact='')
            .order_by('company_id', 'codigo')
        )

        sin_cambios = 0
        a_normalizar = []
        con_error = []

        for cliente in clientes:
            original = cliente.telefono
            try:
                normalizado = normalizar_telefono_ar(original)
            except TelefonoInvalidoException as exc:
                con_error.append((cliente, original, str(exc)))
                continue
            if normalizado == original:
                sin_cambios += 1
                continue
            a_normalizar.append((cliente, original, normalizado))

        total = clientes.count()
        self.stdout.write(f'Clientes con telefono cargado: {total}')
        self.stdout.write(f'  Ya en formato internacional: {sin_cambios}')
        self.stdout.write(f'  A normalizar: {len(a_normalizar)}')
        self.stdout.write(f'  No se pudieron normalizar (requieren revision manual): {len(con_error)}')

        if a_normalizar:
            self.stdout.write('')
            titulo = '-- Normalizando --' if aplicar else '-- Se normalizarian (dry-run) --'
            self.stdout.write(self.style.WARNING(titulo))
            for cliente, original, normalizado in a_normalizar:
                self.stdout.write(
                    f'  [company={cliente.company_id}] {cliente.codigo} {cliente.nombre}: '
                    f'"{original}" -> "{normalizado}"'
                )

        if con_error:
            self.stdout.write('')
            self.stdout.write(self.style.ERROR('-- No se pudieron normalizar (revisar a mano) --'))
            for cliente, original, motivo in con_error:
                self.stdout.write(
                    f'  [company={cliente.company_id}] {cliente.codigo} {cliente.nombre}: '
                    f'"{original}" -- {motivo}'
                )

        if not aplicar:
            self.stdout.write('')
            self.stdout.write(self.style.NOTICE(
                'Modo dry-run: no se guardo nada. Correr con --apply para aplicar estos cambios.'
            ))
            return

        with transaction.atomic():
            for cliente, original, normalizado in a_normalizar:
                cliente.telefono = normalizado
                cliente.save(update_fields=['telefono'])

        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS(f'{len(a_normalizar)} telefonos normalizados y guardados.'))
