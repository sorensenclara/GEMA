import os

from django.test import SimpleTestCase

from reports.services.branding import DEFAULT_LOGO_PATH, resolve_logo_path, resolve_logo_uri


class DefaultLogoPathTests(SimpleTestCase):
    def test_default_logo_path_exists_on_disk(self):
        """Regresión: al mover branding.py a reports/services/ en la
        migración a capas, la ruta relativa al logo quedó apuntando a
        reports/services/assets/ (inexistente) en vez de reports/assets/.
        WeasyPrint no falla si la imagen no existe -- solo la omite en
        silencio -- así que el bug no se notaba en los PDFs generados."""
        self.assertTrue(os.path.exists(DEFAULT_LOGO_PATH))

    def test_resolve_logo_path_without_company_returns_default(self):
        self.assertEqual(resolve_logo_path(None), DEFAULT_LOGO_PATH)

    def test_resolve_logo_uri_without_company_is_a_file_uri_to_existing_file(self):
        uri = resolve_logo_uri(None)
        self.assertTrue(uri.startswith('file://'))
        self.assertTrue(uri.endswith('gema-logo.png'))
