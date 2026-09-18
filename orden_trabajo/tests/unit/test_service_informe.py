from datetime import date

from django.test import TestCase

from orden_trabajo.exceptions import (
    RangoDeFechasInvalidoException,
    SinHistorialParaInformeException,
    SinRecargasParaInformeException,
)
from orden_trabajo.models import Ordenes_de_trabajo
from orden_trabajo.services import emitir_informe_historico_matafuego, emitir_informe_orden, emitir_informe_recargas
from orden_trabajo.tests.factories import OrdenesDeTrabajoFactory, TareaFactory, TareaOrdenFactory


class EmitirInformeOrdenTests(TestCase):
    def test_returns_valid_pdf_bytes(self):
        orden = OrdenesDeTrabajoFactory()
        pdf_bytes = emitir_informe_orden(orden)
        self.assertTrue(pdf_bytes.startswith(b'%PDF'))


class EmitirInformeRecargasTests(TestCase):
    def test_raises_when_range_invalid(self):
        with self.assertRaises(RangoDeFechasInvalidoException):
            emitir_informe_recargas(Ordenes_de_trabajo.objects.none(), '2024-06-01', '2024-01-01')

    def test_raises_when_no_ordenes(self):
        with self.assertRaises(SinRecargasParaInformeException):
            emitir_informe_recargas(Ordenes_de_trabajo.objects.none(), '2024-01-01', '2024-06-01')

    def test_returns_valid_pdf_and_includes_tarea_de_recarga(self):
        orden = OrdenesDeTrabajoFactory(estado='i', fecha_cierre=date(2024, 1, 10))
        TareaOrdenFactory(orden=orden, tarea=TareaFactory(company=orden.company, es_recarga=True, nombre='Recarga'))
        TareaOrdenFactory(orden=orden, tarea=TareaFactory(company=orden.company, es_recarga=False, nombre='Inspección'))

        pdf_bytes = emitir_informe_recargas(
            Ordenes_de_trabajo.objects.filter(pk=orden.pk), '2024-01-01', '2024-01-31',
        )

        self.assertTrue(pdf_bytes.startswith(b'%PDF'))


class EmitirInformeHistoricoMatafuegoTests(TestCase):
    def test_raises_when_matafuego_sin_ordenes_cerradas(self):
        orden = OrdenesDeTrabajoFactory(fecha_cierre=None)

        with self.assertRaises(SinHistorialParaInformeException):
            emitir_informe_historico_matafuego(orden.matafuegos)

    def test_ignora_ordenes_sin_fecha_de_cierre(self):
        matafuego = OrdenesDeTrabajoFactory(fecha_cierre=None).matafuegos
        cerrada = OrdenesDeTrabajoFactory(matafuegos=matafuego, fecha_cierre=date(2024, 1, 10))
        TareaOrdenFactory(orden=cerrada, tarea=TareaFactory(company=matafuego.company, nombre='Inspección'))

        pdf_bytes = emitir_informe_historico_matafuego(matafuego)

        self.assertTrue(pdf_bytes.startswith(b'%PDF'))

    def test_incluye_tareas_de_recarga_y_no_recarga_de_varias_ordenes(self):
        matafuego = OrdenesDeTrabajoFactory(fecha_cierre=None).matafuegos
        vieja = OrdenesDeTrabajoFactory(
            matafuegos=matafuego, estado='i', fecha_cierre=date(2023, 1, 10), numero_dps='d1',
        )
        TareaOrdenFactory(orden=vieja, tarea=TareaFactory(company=matafuego.company, es_recarga=True, nombre='Recarga'))
        reciente = OrdenesDeTrabajoFactory(
            matafuegos=matafuego, estado='i', fecha_cierre=date(2024, 1, 10), numero_dps='d2',
        )
        TareaOrdenFactory(orden=reciente, tarea=TareaFactory(company=matafuego.company, es_recarga=True, nombre='Recarga'))
        TareaOrdenFactory(orden=reciente, tarea=TareaFactory(company=matafuego.company, es_recarga=False, nombre='Inspección'))

        pdf_bytes = emitir_informe_historico_matafuego(matafuego)

        self.assertTrue(pdf_bytes.startswith(b'%PDF'))
