from django.test import SimpleTestCase

from reports.services import render_report_pdf, report_header_context


class RenderReportPdfTests(SimpleTestCase):
    def test_returns_valid_pdf_bytes(self):
        context = report_header_context(None, 'Informe de prueba')
        pdf_bytes = render_report_pdf('reports/_base.html', context)
        self.assertTrue(pdf_bytes.startswith(b'%PDF'))
