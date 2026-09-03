from django.test import TestCase

from orden_trabajo.selectors import calcular_monto
from orden_trabajo.tests.factories import OrdenesDeTrabajoFactory, TareaFactory, TareaOrdenFactory


class CalcularMontoTests(TestCase):
    def test_sums_tarea_precio_when_no_precio_ajustado(self):
        orden = OrdenesDeTrabajoFactory()
        TareaOrdenFactory(orden=orden, tarea=TareaFactory(precio=100), precioAj=0)
        TareaOrdenFactory(orden=orden, tarea=TareaFactory(precio=200), precioAj=0)

        self.assertEqual(calcular_monto(orden), 300)

    def test_uses_precio_ajustado_when_set(self):
        orden = OrdenesDeTrabajoFactory()
        TareaOrdenFactory(orden=orden, tarea=TareaFactory(precio=100), precioAj=50)

        self.assertEqual(calcular_monto(orden), 50)

    def test_returns_zero_without_tareas(self):
        orden = OrdenesDeTrabajoFactory()
        self.assertEqual(calcular_monto(orden), 0)
