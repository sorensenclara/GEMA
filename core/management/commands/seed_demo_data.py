import random
from datetime import date, timedelta

from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from accounts.models import Role, User
from cliente.models import Cliente
from empresas.models import Company
from matafuegos.models import Matafuegos, MarcaMatafuegos, TipoMatafuegos
from orden_trabajo.models import Ordenes_de_trabajo, Tarea, TareaOrden

COMPANY_ID = 1

ADMIN_USERNAME = 'admin_fenix'
ADMIN_EMAIL = 'prueba_fenix@geneos.com.ar'
ADMIN_PASSWORD = 'demo1234'

SUPERUSER_USERNAME = 'admin'
SUPERUSER_EMAIL = 'admingeneos@geneos.com.ar'
SUPERUSER_PASSWORD = 'demo1234'

# Tal como aparecen en la lista de tareas de la app. "Carga" es la unica
# marcada como tarea de recarga (es_recarga=True): habilita la emision de
# la oblea DPS al finalizar una orden (ver orden_trabajo/services/oblea.py).
TAREAS = [
    ('MANGUERA C/MALLA ACERO', 8000, False),
    ('AFFF X LTS', 3500, False),
    ('TOBERA', 4500, False),
    ('HCFC LITRO', 6000, False),
    ('AK LITRO', 5000, False),
    ('KILOGRAMO CO2', 4000, False),
    ('Valvula', 7000, False),
    ('Vastago', 3000, False),
    ('Manguera', 6000, False),
    ('Oring', 500, False),
    ('Kilogramo Polvo', 2500, False),
    ('DPS / Tarjeta de pol y seg amb', 1500, False),
    ('Pintura', 2000, False),
    ('Suncho plástico', 300, False),
    ('Calco', 800, False),
    ('Manómetro', 5500, False),
    ('Prueba Hidráulica', 9000, False),
    ('Control y mantenimiento', 3500, False),
    ('Carga', 12000, True),
]

CLIENTES = [
    ('CLI-001', 'e', 'Panaderia La Espiga', 'Roberto Aguirre'),
    ('CLI-002', 'p', 'Juan Carlos Perez', None),
    ('CLI-003', 'e', 'Supermercado Don Bosco', 'Silvia Ibarra'),
    ('CLI-004', 'p', 'Maria Fernanda Gomez', None),
    ('CLI-005', 'e', 'Transportes del Sur SA', 'Diego Cabral'),
    ('CLI-006', 'e', 'Taller Mecanico Rodriguez', 'Hugo Rodriguez'),
    ('CLI-007', 'p', 'Ana Lucia Fernandez', None),
    ('CLI-008', 'e', 'Farmacia Central', 'Patricia Molina'),
    ('CLI-009', 'p', 'Carlos Alberto Sosa', None),
    ('CLI-010', 'e', 'Distribuidora Norte SRL', 'Marcos Villalba'),
]

ORDEN_ESTADOS_CICLO = ['p', 'ep', 'f', 'i', 'fac', 'c']


class Command(BaseCommand):
    help = 'Genera datos de prueba: tareas, clientes, matafuegos y ordenes de trabajo de ejemplo'

    def handle(self, *args, **options):
        random.seed(2024)

        try:
            company = Company.objects.get(pk=COMPANY_ID)
        except Company.DoesNotExist:
            raise CommandError(f'No existe una Company con id={COMPANY_ID}')

        call_command('import_categorias')
        call_command('import_marcas')
        call_command('import_tipos_matafuegos')

        with transaction.atomic():
            superuser = self._crear_superusuario()
            admin_user = self._crear_usuario_admin(company)
            tareas = self._crear_tareas(company)
            clientes = self._crear_clientes(company)
            matafuegos = self._crear_matafuegos(company, clientes)
            ordenes = self._crear_ordenes(company, matafuegos, tareas)

        self.stdout.write(self.style.SUCCESS(
            f'Listo: superusuario "{superuser.username}", usuario "{admin_user.username}", '
            f'{len(tareas)} tareas, {len(clientes)} clientes, '
            f'{len(matafuegos)} matafuegos, {len(ordenes)} ordenes de trabajo '
            f'para "{company.nombre}".'
        ))

    def _crear_superusuario(self):
        user, created = User.objects.get_or_create(
            username=SUPERUSER_USERNAME,
            defaults={'email': SUPERUSER_EMAIL},
        )
        user.email = SUPERUSER_EMAIL
        user.is_staff = True
        user.is_superuser = True
        user.is_active = True
        user.set_password(SUPERUSER_PASSWORD)
        user.save()
        return user

    def _crear_usuario_admin(self, company):
        user, created = User.objects.get_or_create(
            username=ADMIN_USERNAME,
            defaults={
                'email': ADMIN_EMAIL,
                'company': company,
                'role': Role.ADMIN_EMPRESA,
            },
        )
        if not created:
            user.email = ADMIN_EMAIL
            user.company = company
            user.role = Role.ADMIN_EMPRESA
            user.cliente = None
        user.is_active = True
        user.set_password(ADMIN_PASSWORD)
        user.save()
        return user

    def _crear_tareas(self, company):
        tareas = {}
        for nombre, precio, es_recarga in TAREAS:
            tarea, _ = Tarea.objects.get_or_create(
                company=company,
                nombre=nombre,
                defaults={'precio': precio, 'es_recarga': es_recarga},
            )
            tareas[nombre] = tarea
        return tareas

    def _crear_clientes(self, company):
        clientes = []
        for codigo, tipo, nombre, contacto in CLIENTES:
            slug = codigo.lower()
            cliente, _ = Cliente.objects.get_or_create(
                company=company,
                codigo=codigo,
                defaults={
                    'nombre': nombre,
                    'tipo': tipo,
                    'contacto': contacto,
                    'direccion': f'Calle Falsa {100 + len(clientes) * 10}',
                    'telefono': f'011-4{500 + len(clientes)}-{1000 + len(clientes)}',
                    'email': f'{slug}@ejemplo.com',
                    'estado': 'a',
                },
            )
            clientes.append(cliente)
        return clientes

    def _crear_matafuegos(self, company, clientes):
        tipos = list(TipoMatafuegos.objects.all())
        marcas = list(MarcaMatafuegos.objects.all())
        if not tipos or not marcas:
            raise CommandError('No hay TipoMatafuegos/MarcaMatafuegos cargados. Corre los comandos import_* primero.')

        today = date.today()
        matafuegos = []
        numero = 9000
        for i, cliente in enumerate(clientes):
            cantidad = 2 if i % 3 == 0 else 1
            for j in range(cantidad):
                numero += 1
                fecha_fabricacion = today - timedelta(days=800 + (numero % 400))
                fecha_carga = today - timedelta(days=30 + (numero % 500))
                fecha_ph = today - timedelta(days=60 + (numero % 400))

                # Escalonamos vencimientos: algunos ya vencidos, algunos
                # proximos a vencer (para que aparezcan en los informes de
                # alerta/proximos vencimientos), y otros lejanos.
                offset_carga = -20 + (numero * 7) % 90
                offset_ph = -15 + (numero * 11) % 120
                fecha_proxima_carga = today + timedelta(days=offset_carga)
                fecha_proxima_ph = today + timedelta(days=offset_ph)

                categoria = 'v' if numero % 5 == 0 else ('ma' if numero % 11 == 0 else 'd')
                patente = f'AB{numero % 1000:03d}CD' if categoria == 'v' else None

                mat, created = Matafuegos.objects.get_or_create(
                    company=company,
                    numero=numero,
                    defaults={
                        'cliente': cliente,
                        'patente': patente,
                        'direccion': cliente.direccion,
                        'localizacion': 'Planta baja' if j == 0 else 'Primer piso',
                        'marca': marcas[numero % len(marcas)],
                        'tipo': tipos[numero % len(tipos)],
                        'categoria': categoria,
                        'fecha_fabricacion': fecha_fabricacion,
                        'fecha_carga': fecha_carga,
                        'fecha_ph': fecha_ph,
                        'estado': 'a',
                    },
                )
                if created:
                    mat.fecha_proxima_carga = fecha_proxima_carga
                    mat.fecha_proxima_ph = fecha_proxima_ph
                    mat.vencido = fecha_proxima_carga < today or fecha_proxima_ph < today
                    mat.save()
                matafuegos.append(mat)
        return matafuegos

    def _crear_ordenes(self, company, matafuegos, tareas):
        today = date.today()
        carga = tareas['Carga']
        ph = tareas['Prueba Hidráulica']
        mantenimiento = tareas['Control y mantenimiento']
        otras = [t for nombre, t in tareas.items() if nombre not in ('Carga', 'Prueba Hidráulica', 'Control y mantenimiento')]

        ordenes = []
        for i, mat in enumerate(matafuegos):
            estado = ORDEN_ESTADOS_CICLO[i % len(ORDEN_ESTADOS_CICLO)]
            notas = f'Orden de prueba #{i + 1}'

            orden, created = Ordenes_de_trabajo.objects.get_or_create(
                company=company,
                cliente=mat.cliente,
                matafuegos=mat,
                notas=notas,
                defaults={
                    'fecha_creacion': today - timedelta(days=10 + i),
                    'fecha_inicio': today - timedelta(days=9 + i),
                    'fecha_entrega': today - timedelta(days=2 + i),
                    'estado': estado,
                    'usuario': 'demo',
                },
            )
            if not created:
                ordenes.append(orden)
                continue

            cerrada = estado in ('f', 'i', 'fac')
            if cerrada:
                # La mitad de las cerradas quedan dentro de la ultima
                # semana, para poblar el informe de facturacion semanal.
                dias_atras = 2 + (i % 5) if i % 2 == 0 else 20 + (i % 40)
                orden.fecha_cierre = today - timedelta(days=dias_atras)

            tareas_orden = [mantenimiento, otras[i % len(otras)]]
            if estado == 'i' or (estado == 'fac' and i % 2 == 0):
                # Tarea de recarga: habilita numero_dps, como si se hubiera
                # emitido la oblea (ver oblea.py: es_recarga=True requerido).
                tareas_orden.append(carga)
                dps = f'{company.numero_recargador or "000"}-{1000 + i}'
                orden.numero_dps = dps
                mat.numero_dps = dps
                mat.fecha_carga = orden.fecha_cierre or mat.fecha_carga
                mat.save()
            if i % 4 == 0:
                tareas_orden.append(ph)

            monto_total = 0
            for tarea in tareas_orden:
                cant_cargada = mat.tipo.volumen if tarea is carga and mat.tipo.volumen else 1
                TareaOrden.objects.get_or_create(
                    tarea=tarea,
                    orden=orden,
                    defaults={'precioAj': 0, 'cant_cargada': cant_cargada},
                )
                monto_total += tarea.precio
            orden.monto_total = monto_total
            orden.save()
            ordenes.append(orden)
        return ordenes
