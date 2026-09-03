from django.test import TestCase

from orden_trabajo.services import emitir_informe_orden
from orden_trabajo.tests.factories import OrdenesDeTrabajoFactory


class EmitirInformeOrdenTests(TestCase):
    def test_returns_valid_pdf_bytes(self):
        orden = OrdenesDeTrabajoFactory()
        pdf_bytes = emitir_informe_orden(orden)
        self.assertTrue(pdf_bytes.startswith(b'%PDF'))
