from django.test import TestCase

from orden_trabajo.exceptions import SinOrdenesParaFacturarException
from orden_trabajo.models import Ordenes_de_trabajo
from orden_trabajo.services import emitir_informe_facturacion, emitir_informe_facturacion_ultima_semana
from orden_trabajo.services.facturacion import _agregar_tareas_por_cliente, _precio_efectivo
from orden_trabajo.tests.factories import OrdenesDeTrabajoFactory, TareaFactory, TareaOrdenFactory


class EmitirInformeFacturacionTests(TestCase):
    def test_raises_when_no_ordenes(self):
        with self.assertRaises(SinOrdenesParaFacturarException):
            emitir_informe_facturacion(Ordenes_de_trabajo.objects.none())

    def test_returns_valid_pdf_with_ordenes(self):
        orden = OrdenesDeTrabajoFactory()
        TareaOrdenFactory(orden=orden, tarea=TareaFactory())

        pdf_bytes = emitir_informe_facturacion(Ordenes_de_trabajo.objects.filter(pk=orden.pk))

        self.assertTrue(pdf_bytes.startswith(b'%PDF'))


class PrecioEfectivoTests(TestCase):
    def test_usa_precio_de_la_tarea_cuando_no_hay_ajuste(self):
        t = TareaOrdenFactory(tarea=TareaFactory(precio=100), precioAj=0)
        self.assertEqual(_precio_efectivo(t), 100)

    def test_usa_precio_ajustado_cuando_esta_cargado(self):
        t = TareaOrdenFactory(tarea=TareaFactory(precio=100), precioAj=80)
        self.assertEqual(_precio_efectivo(t), 80)


class AgregarTareasPorClienteTests(TestCase):
    def test_totaliza_precio_por_combinacion_repetida(self):
        orden = OrdenesDeTrabajoFactory()
        tarea = TareaFactory(precio=150)
        TareaOrdenFactory(orden=orden, tarea=tarea, cant_cargada=1)
        TareaOrdenFactory(orden=orden, tarea=tarea, cant_cargada=1)

        conteo, subtotales = _agregar_tareas_por_cliente([orden])

        clave = (tarea.nombre, '1.0', str(orden.matafuegos.tipo))
        self.assertEqual(conteo[clave], 2)
        self.assertEqual(subtotales[clave], 300)


class EmitirInformeFacturacionUltimaSemanaTests(TestCase):
    def test_raises_when_no_ordenes(self):
        with self.assertRaises(SinOrdenesParaFacturarException):
            emitir_informe_facturacion_ultima_semana(Ordenes_de_trabajo.objects.none())

    def test_returns_valid_pdf_with_ordenes(self):
        orden = OrdenesDeTrabajoFactory()
        TareaOrdenFactory(orden=orden, tarea=TareaFactory())

        pdf_bytes = emitir_informe_facturacion_ultima_semana(Ordenes_de_trabajo.objects.filter(pk=orden.pk))

        self.assertTrue(pdf_bytes.startswith(b'%PDF'))
