from django.db import migrations


NOMBRE_COMPANIA_INICIAL = "Seguridad Fenix"


def crear_compania_inicial_y_backfill(apps, schema_editor):
    Company = apps.get_model('empresas', 'Company')
    Parametros = apps.get_model('parametros', 'Parametros')
    Cliente = apps.get_model('cliente', 'Cliente')
    Matafuegos = apps.get_model('matafuegos', 'Matafuegos')
    Tarea = apps.get_model('orden_trabajo', 'Tarea')
    OrdenesDeTrabajo = apps.get_model('orden_trabajo', 'Ordenes_de_trabajo')
    User = apps.get_model('accounts', 'User')

    parametros = Parametros.objects.first()
    company = Company.objects.create(
        nombre=NOMBRE_COMPANIA_INICIAL,
        veh_inicio=parametros.veh_inicio if parametros else 0,
        veh_fin=parametros.veh_fin if parametros else 0,
        veh_prefijo=parametros.veh_prefijo if parametros else "",
        veh_actual=parametros.veh_actual if parametros else 0,
        dom_inicio=parametros.dom_inicio if parametros else 0,
        dom_fin=parametros.dom_fin if parametros else 0,
        dom_prefijo=parametros.dom_prefijo if parametros else "",
        dom_actual=parametros.dom_actual if parametros else 0,
        smtp_email=parametros.email if parametros else None,
        smtp_password=parametros.password if parametros else None,
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
        # Solo necesita que exista la fila de Parametros (creada en 0002); no
        # depender de 0003/0004 evita un ciclo con la migración de swap de PK
        # de Cliente (que depende de accounts, que a su vez usa el User model
        # completo en parametros.0004).
        ('parametros', '0002_auto_20220531_1344'),
        ('cliente', '0015_cliente_company'),
        ('matafuegos', '0025_matafuegos_company'),
        ('orden_trabajo', '0011_ordenes_de_trabajo_company_tarea_company'),
        ('accounts', '0002_user_company_role_cliente'),
    ]

    operations = [
        migrations.RunPython(crear_compania_inicial_y_backfill, migrations.RunPython.noop),
    ]
