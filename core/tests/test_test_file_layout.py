"""Guarda que ninguna app vuelva a tener un `test_*.py`/`tests.py` plano en
su raíz en vez de `tests/unit/` + `tests/integration/` + `tests/factories/`
(ver CLAUDE.md del boilerplate de referencia y el plan de migración a capas).
Se agrega al final de la migración, una vez que todas las apps ya tienen el
layout nuevo -- agregarlo antes rompería el build de las apps aún sin migrar."""
from pathlib import Path

from django.apps import apps as django_apps
from django.conf import settings
from django.test import SimpleTestCase


class TestFileLayoutTests(SimpleTestCase):
    def test_no_flat_test_files_at_any_app_root(self):
        base_dir = Path(settings.BASE_DIR)
        offenders = []

        for app_config in django_apps.get_app_configs():
            app_path = Path(app_config.path)
            # Las apps locales son carpetas top-level bajo la raíz del proyecto
            # (accounts/, cliente/, ...). El resto -- apps de Django/terceros --
            # vive dentro de .venv/ (que también cuelga de BASE_DIR, así que un
            # relative_to() simple no alcanza para excluirlas).
            if app_path.parent != base_dir:
                continue

            for f in sorted(app_path.glob("test_*.py")):
                offenders.append(str(f.relative_to(base_dir)))

            tests_py = app_path / "tests.py"
            if tests_py.exists():
                offenders.append(str(tests_py.relative_to(base_dir)))

        self.assertEqual(
            offenders, [],
            "Estos archivos están planos en la raíz de una app en vez de en "
            "tests/unit/ o tests/integration/ (incluye el stub tests.py "
            "default de Django, que debe borrarse apenas la app tiene tests "
            "reales): " + ", ".join(offenders)
        )
