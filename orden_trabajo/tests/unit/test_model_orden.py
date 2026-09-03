from django.test import TestCase

from orden_trabajo.tests.factories import OrdenesDeTrabajoFactory


class OrdenesDeTrabajoFieldsTests(TestCase):
    def test_field_labels(self):
        orden = OrdenesDeTrabajoFactory()
        labels = {
            'fecha_creacion': 'Fecha de creacion de orden',
            'fecha_inicio': 'Fecha de inicio',
            'fecha_entrega': 'Entrega estimada',
            'fecha_cierre': 'Fecha de cierre',
            'cliente': 'Cliente',
            'matafuegos': 'Matafuegos',
            'estado': 'Estado',
            'monto_total': 'Monto',
            'notas': 'Notas',
            'usuario': 'Usuario responsable',
        }
        for field_name, expected in labels.items():
            with self.subTest(field=field_name):
                self.assertEqual(orden._meta.get_field(field_name).verbose_name, expected)

    def test_field_max_lengths(self):
        orden = OrdenesDeTrabajoFactory()
        self.assertEqual(orden._meta.get_field('estado').max_length, 80)
        self.assertEqual(orden._meta.get_field('notas').max_length, 80)
        self.assertEqual(orden._meta.get_field('usuario').max_length, 30)

    def test_str_returns_id(self):
        orden = OrdenesDeTrabajoFactory()
        self.assertEqual(str(orden), str(orden.id))
