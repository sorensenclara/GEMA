from datetime import date

from django.test import TestCase

from orden_trabajo.exceptions import (
    CategoriaOrdenInvalidaException,
    OrdenNoFinalizadaException,
    OrdenSinFechaCierreException,
    OrdenSinTareaDeRecargaException,
)
from orden_trabajo.models import Ordenes_de_trabajo
from orden_trabajo.services import emitir_oblea_domiciliaria, emitir_oblea_vehicular
from orden_trabajo.services.oblea import _campos_oblea_domiciliaria, _campos_oblea_vehicular
from orden_trabajo.tests.factories import OrdenesDeTrabajoFactory, TareaFactory, TareaOrdenFactory


def _orden_lista_para_oblea(categoria, company=None):
    kwargs = {'matafuegos__categoria': categoria, 'estado': 'f', 'fecha_cierre': date(2022, 4, 28)}
    if company is not None:
        kwargs['matafuegos__cliente__company'] = company
    orden = OrdenesDeTrabajoFactory(**kwargs)
    TareaOrdenFactory(orden=orden, tarea=TareaFactory(company=orden.company, es_recarga=True))
    return orden


class EmitirObleaVehicularTests(TestCase):
    def test_permite_imprimir_una_sola_orden(self):
        orden = _orden_lista_para_oblea('v')

        pdf_bytes = emitir_oblea_vehicular(Ordenes_de_trabajo.objects.filter(pk=orden.pk))

        self.assertTrue(pdf_bytes.startswith(b'%PDF'))
        orden.refresh_from_db()
        self.assertEqual(orden.estado, 'i')
        self.assertTrue(orden.numero_dps)

    def test_raises_when_categoria_invalida(self):
        orden1 = _orden_lista_para_oblea('d')
        orden2 = _orden_lista_para_oblea('d', company=orden1.company)
        with self.assertRaises(CategoriaOrdenInvalidaException):
            emitir_oblea_vehicular(Ordenes_de_trabajo.objects.filter(pk__in=[orden1.pk, orden2.pk]))

    def test_raises_when_orden_no_finalizada(self):
        orden1 = _orden_lista_para_oblea('v')
        orden1.estado = 'p'
        orden1.save()
        orden2 = _orden_lista_para_oblea('v', company=orden1.company)
        with self.assertRaises(OrdenNoFinalizadaException):
            emitir_oblea_vehicular(Ordenes_de_trabajo.objects.filter(pk__in=[orden1.pk, orden2.pk]))

    def test_raises_when_sin_fecha_cierre(self):
        orden1 = _orden_lista_para_oblea('v')
        orden1.fecha_cierre = None
        orden1.save()
        orden2 = _orden_lista_para_oblea('v', company=orden1.company)
        with self.assertRaises(OrdenSinFechaCierreException):
            emitir_oblea_vehicular(Ordenes_de_trabajo.objects.filter(pk__in=[orden1.pk, orden2.pk]))

    def test_raises_when_sin_tarea_de_recarga(self):
        orden1 = OrdenesDeTrabajoFactory(matafuegos__categoria='v', estado='f', fecha_cierre=date(2022, 4, 28))
        orden2 = _orden_lista_para_oblea('v', company=orden1.company)
        with self.assertRaises(OrdenSinTareaDeRecargaException):
            emitir_oblea_vehicular(Ordenes_de_trabajo.objects.filter(pk__in=[orden1.pk, orden2.pk]))

    def test_happy_path_marks_impresa_and_returns_pdf(self):
        orden1 = _orden_lista_para_oblea('v')
        orden2 = _orden_lista_para_oblea('v', company=orden1.company)

        pdf_bytes = emitir_oblea_vehicular(Ordenes_de_trabajo.objects.filter(pk__in=[orden1.pk, orden2.pk]))

        self.assertTrue(pdf_bytes.startswith(b'%PDF'))
        orden1.refresh_from_db()
        orden2.refresh_from_db()
        self.assertEqual(orden1.estado, 'i')
        self.assertEqual(orden2.estado, 'i')
        orden1.matafuegos.refresh_from_db()
        self.assertTrue(orden1.matafuegos.numero_dps)
        self.assertEqual(orden1.matafuegos.fecha_carga, orden1.fecha_cierre)
        self.assertEqual(orden1.numero_dps, orden1.matafuegos.numero_dps)
        self.assertEqual(orden2.numero_dps, orden2.matafuegos.numero_dps)

    def test_campos_incluyen_numero_recargador_de_la_company(self):
        orden = _orden_lista_para_oblea('v')
        orden.company.numero_recargador = '150'
        orden.company.save()

        textos = [c['texto'] for c in _campos_oblea_vehicular(orden, x=0, y=0)]

        self.assertIn('150', textos)


class EmitirObleaDomiciliariaTests(TestCase):
    def test_permite_imprimir_una_sola_orden(self):
        orden = _orden_lista_para_oblea('d')

        pdf_bytes = emitir_oblea_domiciliaria(Ordenes_de_trabajo.objects.filter(pk=orden.pk))

        self.assertTrue(pdf_bytes.startswith(b'%PDF'))
        orden.refresh_from_db()
        self.assertEqual(orden.estado, 'i')
        self.assertTrue(orden.numero_dps)

    def test_returns_valid_pdf_for_three_ordenes_con_ultima_pagina_incompleta(self):
        ordenes = [_orden_lista_para_oblea('d')]
        company = ordenes[0].company
        ordenes += [_orden_lista_para_oblea('d', company=company) for _ in range(2)]

        pdf_bytes = emitir_oblea_domiciliaria(
            Ordenes_de_trabajo.objects.filter(pk__in=[o.pk for o in ordenes])
        )

        self.assertTrue(pdf_bytes.startswith(b'%PDF'))
        for orden in ordenes:
            orden.refresh_from_db()
            self.assertEqual(orden.estado, 'i')
            self.assertTrue(orden.numero_dps)

    def test_raises_when_categoria_invalida(self):
        orden1 = _orden_lista_para_oblea('v')
        orden2 = _orden_lista_para_oblea('v', company=orden1.company)
        with self.assertRaises(CategoriaOrdenInvalidaException):
            emitir_oblea_domiciliaria(Ordenes_de_trabajo.objects.filter(pk__in=[orden1.pk, orden2.pk]))

    def test_happy_path_marks_impresa_and_returns_pdf(self):
        orden1 = _orden_lista_para_oblea('d')
        orden2 = _orden_lista_para_oblea('d', company=orden1.company)

        pdf_bytes = emitir_oblea_domiciliaria(Ordenes_de_trabajo.objects.filter(pk__in=[orden1.pk, orden2.pk]))

        self.assertTrue(pdf_bytes.startswith(b'%PDF'))
        orden1.refresh_from_db()
        self.assertEqual(orden1.estado, 'i')
        orden1.matafuegos.refresh_from_db()
        self.assertTrue(orden1.matafuegos.numero_dps)
        self.assertEqual(orden1.numero_dps, orden1.matafuegos.numero_dps)

    def test_campos_incluyen_numero_recargador_de_la_company(self):
        orden = _orden_lista_para_oblea('d')
        orden.company.numero_recargador = '150'
        orden.company.save()

        textos = [c['texto'] for c in _campos_oblea_domiciliaria(orden, x=0, y=0)]

        self.assertIn('150', textos)

    def test_returns_valid_pdf_for_four_ordenes_across_two_pages(self):
        ordenes = [_orden_lista_para_oblea('d')]
        company = ordenes[0].company
        ordenes += [_orden_lista_para_oblea('d', company=company) for _ in range(3)]

        pdf_bytes = emitir_oblea_domiciliaria(
            Ordenes_de_trabajo.objects.filter(pk__in=[o.pk for o in ordenes])
        )

        self.assertTrue(pdf_bytes.startswith(b'%PDF'))
