from datetime import date

from django.test import TestCase

from orden_trabajo.exceptions import TransicionDeEstadoInvalidaException
from orden_trabajo.services import cancelar_orden, facturar_orden, finalizar_orden, iniciar_orden, recalcular_monto_total
from orden_trabajo.tests.factories import OrdenesDeTrabajoFactory, TareaFactory, TareaOrdenFactory


class RecalcularMontoTotalTests(TestCase):
    def test_updates_and_persists_monto_total(self):
        orden = OrdenesDeTrabajoFactory(monto_total=0)
        TareaOrdenFactory(orden=orden, tarea=TareaFactory(precio=150), precioAj=0)

        recalcular_monto_total(orden)

        orden.refresh_from_db()
        self.assertEqual(orden.monto_total, 150)


class IniciarOrdenTests(TestCase):
    def test_pendiente_pasa_a_en_proceso(self):
        orden = OrdenesDeTrabajoFactory(estado='p')

        iniciar_orden(orden)

        orden.refresh_from_db()
        self.assertEqual(orden.estado, 'ep')

    def test_raises_when_no_esta_pendiente(self):
        orden = OrdenesDeTrabajoFactory(estado='ep')

        with self.assertRaises(TransicionDeEstadoInvalidaException):
            iniciar_orden(orden)


class FinalizarOrdenTests(TestCase):
    def test_en_proceso_pasa_a_finalizada_con_fecha_de_hoy(self):
        orden = OrdenesDeTrabajoFactory(estado='ep', fecha_cierre=None)

        finalizar_orden(orden)

        orden.refresh_from_db()
        self.assertEqual(orden.estado, 'f')
        self.assertEqual(orden.fecha_cierre, date.today())

    def test_raises_when_no_esta_en_proceso(self):
        orden = OrdenesDeTrabajoFactory(estado='p')

        with self.assertRaises(TransicionDeEstadoInvalidaException):
            finalizar_orden(orden)


class CancelarOrdenTests(TestCase):
    def test_en_proceso_pasa_a_cancelada(self):
        orden = OrdenesDeTrabajoFactory(estado='ep')

        cancelar_orden(orden)

        orden.refresh_from_db()
        self.assertEqual(orden.estado, 'c')

    def test_raises_when_no_esta_en_proceso(self):
        orden = OrdenesDeTrabajoFactory(estado='f')

        with self.assertRaises(TransicionDeEstadoInvalidaException):
            cancelar_orden(orden)


class FacturarOrdenTests(TestCase):
    def test_impresa_pasa_a_facturada(self):
        orden = OrdenesDeTrabajoFactory(estado='i')

        facturar_orden(orden)

        orden.refresh_from_db()
        self.assertEqual(orden.estado, 'fac')

    def test_raises_when_no_esta_impresa(self):
        orden = OrdenesDeTrabajoFactory(estado='f')

        with self.assertRaises(TransicionDeEstadoInvalidaException):
            facturar_orden(orden)
