import os

from django.test import SimpleTestCase, TestCase

from orden_trabajo.tests.factories import OrdenesDeTrabajoFactory
from reports.services.branding import (
    DEFAULT_LOGO_PATH,
    DEFAULT_NUMERO_RECARGADOR,
    resolve_logo_path,
    resolve_logo_uri,
    resolve_numero_recargador,
)


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


class ResolveNumeroRecargadorTests(TestCase):
    def test_without_company_returns_default(self):
        self.assertEqual(resolve_numero_recargador(None), DEFAULT_NUMERO_RECARGADOR)

    def test_company_without_numero_recargador_returns_default(self):
        orden = OrdenesDeTrabajoFactory(matafuegos__cliente__company__numero_recargador='')
        self.assertEqual(resolve_numero_recargador(orden), DEFAULT_NUMERO_RECARGADOR)

    def test_company_with_numero_recargador_returns_its_own_value(self):
        orden = OrdenesDeTrabajoFactory(matafuegos__cliente__company__numero_recargador='150')
        self.assertEqual(resolve_numero_recargador(orden), '150')
