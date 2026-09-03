from django.db import migrations


NOMBRE_COMPANIA_INICIAL = "Seguridad Fenix"


def crear_compania_inicial_y_backfill(apps, schema_editor):
    Company = apps.get_model('empresas', 'Company')
    Cliente = apps.get_model('cliente', 'Cliente')
    Matafuegos = apps.get_model('matafuegos', 'Matafuegos')
    Tarea = apps.get_model('orden_trabajo', 'Tarea')
    OrdenesDeTrabajo = apps.get_model('orden_trabajo', 'Ordenes_de_trabajo')
    User = apps.get_model('accounts', 'User')

    # La app `parametros` (fuente original de estos valores) ya no existe --
    # eliminada tras migrar sus campos a Company (ver 0001_initial de esta
    # app). Un `migrate` desde cero arranca con los rangos DPS en blanco,
    # igual que ya pasaba acá cuando no había ninguna fila de Parametros.
    company = Company.objects.create(
        nombre=NOMBRE_COMPANIA_INICIAL,
        veh_inicio=0,
        veh_fin=0,
        veh_prefijo="",
        veh_actual=0,
        dom_inicio=0,
        dom_fin=0,
        dom_prefijo="",
        dom_actual=0,
        smtp_email=None,
        smtp_password=None,
    )

    Cliente.objects.update(company=company)
    Matafuegos.objects.update(company=company)
    Tarea.objects.update(company=company)
    OrdenesDeTrabajo.objects.update(company=company)
    # Rol por defecto 'operador' para todo el que ya tenía cuenta; revisar y
    # promover manualmente a 'admin_empresa' a quien corresponda (ver plan).
    User.objects.filter(is_superuser=False).update(company=company, role='operador')


class Migration(migrations.Migration):

    dependencies = [
        ('empresas', '0001_initial'),
        ('cliente', '0015_cliente_company'),
        ('matafuegos', '0025_matafuegos_company'),
        ('orden_trabajo', '0011_ordenes_de_trabajo_company_tarea_company'),
        ('accounts', '0002_user_company_role_cliente'),
    ]

    operations = [
        migrations.RunPython(crear_compania_inicial_y_backfill, migrations.RunPython.noop),
    ]
