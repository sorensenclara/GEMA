from datetime import date, timedelta

from django.test import TestCase
from freezegun import freeze_time

from matafuegos.exceptions import (
    RangoDeFechasInvalidoException,
    SinMatafuegosParaAlertaException,
    SinMatafuegosParaInformeException,
)
from matafuegos.models import Matafuegos
from matafuegos.services import (
    activar_matafuego,
    eliminar_matafuego,
    emitir_alerta_vencimientos,
    emitir_informe_proximos_vencimientos,
    generar_listado_matafuegos,
    marcar_vencidos,
)
from matafuegos.tests.factories import MatafuegosFactory
from orden_trabajo.tests.factories import OrdenesDeTrabajoFactory


class GenerarListadoMatafuegosTests(TestCase):
    def test_returns_valid_pdf_for_empty_queryset(self):
        pdf_bytes = generar_listado_matafuegos([])
        self.assertTrue(pdf_bytes.startswith(b'%PDF'))

    def test_returns_valid_pdf_with_matafuegos(self):
        MatafuegosFactory.create_batch(2)
        pdf_bytes = generar_listado_matafuegos(Matafuegos.objects.all())
        self.assertTrue(pdf_bytes.startswith(b'%PDF'))


class EmitirAlertaVencimientosTests(TestCase):
    def test_raises_when_range_invalid(self):
        with self.assertRaises(RangoDeFechasInvalidoException):
            emitir_alerta_vencimientos(Matafuegos.objects.none(), '2024-06-01', '2024-01-01')

    def test_raises_when_no_matafuegos(self):
        with self.assertRaises(SinMatafuegosParaAlertaException):
            emitir_alerta_vencimientos(Matafuegos.objects.none(), '2024-01-01', '2024-06-01')

    def test_returns_valid_pdf_when_matafuegos_present(self):
        matafuego = MatafuegosFactory()
        pdf_bytes = emitir_alerta_vencimientos(
            Matafuegos.objects.filter(pk=matafuego.pk), '2020-01-01', '2030-01-01',
        )
        self.assertTrue(pdf_bytes.startswith(b'%PDF'))


class EmitirInformeProximosVencimientosTests(TestCase):
    def test_raises_when_no_matafuegos_in_either_group(self):
        with self.assertRaises(SinMatafuegosParaInformeException):
            emitir_informe_proximos_vencimientos(Matafuegos.objects.none(), Matafuegos.objects.none())

    def test_returns_valid_pdf_when_carga_group_has_matafuegos(self):
        matafuego = MatafuegosFactory()
        pdf_bytes = emitir_informe_proximos_vencimientos(
            Matafuegos.objects.filter(pk=matafuego.pk), Matafuegos.objects.none(),
        )
        self.assertTrue(pdf_bytes.startswith(b'%PDF'))


class MarcarVencidosTests(TestCase):
    @freeze_time('2024-01-01')
    def test_marks_matafuegos_older_than_21_years_as_vencido(self):
        viejo = MatafuegosFactory(fecha_fabricacion=date(2024, 1, 1) - timedelta(days=22 * 365))
        nuevo = MatafuegosFactory(fecha_fabricacion=date(2024, 1, 1) - timedelta(days=365))

        marcar_vencidos()

        viejo.refresh_from_db()
        nuevo.refresh_from_db()
        self.assertTrue(viejo.vencido)
        self.assertFalse(nuevo.vencido)


class EliminarMatafuegoTests(TestCase):
    def test_delete_fisico_cuando_no_tiene_ordenes(self):
        matafuego = MatafuegosFactory()

        eliminado = eliminar_matafuego(matafuego)

        self.assertTrue(eliminado)
        self.assertFalse(Matafuegos.objects.filter(pk=matafuego.pk).exists())

    def test_baja_logica_cuando_tiene_ordenes_asociadas(self):
        matafuego = MatafuegosFactory()
        OrdenesDeTrabajoFactory(matafuegos=matafuego)

        eliminado = eliminar_matafuego(matafuego)

        self.assertFalse(eliminado)
        matafuego.refresh_from_db()
        self.assertEqual(matafuego.estado, 'i')


class ActivarMatafuegoTests(TestCase):
    def test_reactiva_un_matafuego_inactivo(self):
        matafuego = MatafuegosFactory(estado='i')

        activar_matafuego(matafuego)

        matafuego.refresh_from_db()
        self.assertEqual(matafuego.estado, 'a')
