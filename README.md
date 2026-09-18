# GEMA — django-matafuegos

Sistema de gestión de matafuegos, clientes y órdenes de trabajo, multi-tenant
por compañía. Migrado al estándar de arquitectura en capas definido en
`django-layered-boilerplate` (ver el plan de migración para el detalle
completo, en el historial de esta rama). Django 5.2, Python 3.12.

Apps de dominio: `empresas` (Company), `accounts` (User/Role), `cliente`,
`matafuegos` (incluye el portal "Mis matafuegos" para el rol cliente final),
`orden_trabajo` (Tarea/Ordenes_de_trabajo, incluye la emisión de obleas DPS).
`core` es infraestructura transversal (auditoría, historial genérico,
dashboard, login/paginación) sin modelos propios de negocio. `reports` es la
capa de renderizado de informes en PDF (WeasyPrint), reusada por las demás.

## Setup

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

git config core.hooksPath .githooks   # una vez por clon, habilita el pre-push hook

cp gema/.env_template gema/.env       # completar con credenciales locales
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

## Tests

```bash
pytest                 # unit + integration (sin E2E todavía)
pytest -m "not e2e"    # equivalente, explícito
```

## Arquitectura en capas

Cada app se organiza en paquetes `models/ services/ selectors/ views/
filters/ forms/ tests/{unit,integration,factories}/`. Ver `core/` como
referencia de la infraestructura transversal (`AuditModel`, excepciones de
dominio, historial genérico).

**Desviación deliberada del boilerplate de referencia:** este proyecto
mantiene un modelo de usuario custom (`accounts.User` + `Role`) en vez de
migrar a `Group`/`Permission` nativo de Django. Los 3 roles determinan qué
portal ve cada usuario dentro de su compañía (multi-tenant), un enrutamiento
estructural que no mapea bien a Groups (globales, sin noción de compañía).
`core/mixins.py::PermissionRequiredMixin` queda disponible para permisos
puntuales no-CRUD (vía `Meta.permissions`), como complemento de
`accounts/mixins.py`, no como reemplazo.

## Migraciones — prevención de conflictos entre desarrolladores

Este proyecto usa **django-linear-migrations**. Cada app tiene un
`migrations/max_migration.txt` con el nombre de su última migración;
`makemigrations` lo actualiza solo — nunca editarlo a mano salvo al resolver
un conflicto.

**Por qué:** Django ordena las migraciones por su grafo de `dependencies`,
no por el número de archivo. Dos ramas que agregan, cada una, una
`0007_x.py` para la misma app sobre la misma base producen dos hojas del
grafo sin orden entre sí — un conflicto de "múltiples migraciones hoja" que
Django recién reporta cuando alguien corre `migrate`, quizás mucho después
del merge. `max_migration.txt` convierte eso en un conflicto de git de una
sola línea, visible en el momento del rebase.

**Si aparece un conflicto en `max_migration.txt` durante un rebase:**

```bash
python manage.py migrate <app> <ultima_migracion_comun>   # desaplicar la migración local primero
git rebase --continue   # tras resolver el resto de los archivos, o antes correr:
python manage.py rebase_migration <app>                    # renumera + redepende la migración, arregla max_migration.txt
git add <app>/migrations
git rebase --continue
python manage.py migrate <app>
```

**Enforcement:**
- Local: `.githooks/pre-push` corre `manage.py check` (incluye los checks
  `dlm.E001`–`E005` de django-linear-migrations) y
  `makemigrations --check --dry-run`. Setup único por clon:
  `git config core.hooksPath .githooks`.
- CI: `.gitlab-ci.yml` corre los mismos dos checks como backstop, ya que el
  hook local se puede saltear o nunca instalarse.

App nueva agregada a `INSTALLED_APPS`: correr
`python manage.py create_max_migration_files <app_label>` una vez, o los
checks van a fallar con `dlm.E001`.

## Workflow: rebase antes de push, no merge

Un `git pull` sin `--rebase` crea un merge commit; `.githooks/pre-push`
bloquea un push que contenga merge commits. Configuración recomendada
(no forzada, solo cambia el default): `git config --global pull.rebase true`.



## Carga de datos

python manage.py import_categorias
python manage.py import_marcas
python manage.py import_tipos_matafuegos


#Para datos de prueba
Clientes, matagueros, tareas y ordenes de trabajo
Las tareas las crea para la empresa con id 1- Matafuegos fenix
python manage.py seed_demo_data