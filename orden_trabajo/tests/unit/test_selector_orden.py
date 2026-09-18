from datetime import date, timedelta

from django.test import TestCase
from freezegun import freeze_time

from empresas.tests.factories import CompanyFactory
from orden_trabajo.selectors import (
    count_ordenes_pendientes,
    list_ordenes,
    list_ordenes_recargadas_entre,
    list_ordenes_ultima_semana,
)
from orden_trabajo.tests.factories import OrdenesDeTrabajoFactory


class ListOrdenesTests(TestCase):
    def test_only_returns_ordenes_of_company(self):
        company = CompanyFactory()
        mia = OrdenesDeTrabajoFactory(matafuegos__cliente__company=company)
        OrdenesDeTrabajoFactory()

        self.assertEqual(list(list_ordenes(company)), [mia])

    def test_filters_by_estado(self):
        company = CompanyFactory()
        pendiente = OrdenesDeTrabajoFactory(matafuegos__cliente__company=company, estado='p')
        OrdenesDeTrabajoFactory(matafuegos__cliente__company=company, estado='f')

        self.assertEqual(list(list_ordenes(company, estado='p')), [pendiente])

    def test_filters_by_tipo_matafuego(self):
        from matafuegos.tests.factories import TipoMatafuegosFactory

        company = CompanyFactory()
        tipo = TipoMatafuegosFactory()
        match = OrdenesDeTrabajoFactory(matafuegos__cliente__company=company, matafuegos__tipo=tipo)
        OrdenesDeTrabajoFactory(matafuegos__cliente__company=company)

        self.assertEqual(list(list_ordenes(company, tipo_matafuego=tipo.pk)), [match])

    def test_filters_by_categoria_matafuego(self):
        company = CompanyFactory()
        match = OrdenesDeTrabajoFactory(matafuegos__cliente__company=company, matafuegos__categoria='v')
        OrdenesDeTrabajoFactory(matafuegos__cliente__company=company, matafuegos__categoria='d')

        self.assertEqual(list(list_ordenes(company, categoria_matafuego='v')), [match])


class CountOrdenesPendientesTests(TestCase):
    def test_counts_only_pendientes_of_company(self):
        company = CompanyFactory()
        OrdenesDeTrabajoFactory(matafuegos__cliente__company=company, estado='p')
        OrdenesDeTrabajoFactory(matafuegos__cliente__company=company, estado='f')

        self.assertEqual(count_ordenes_pendientes(company), 1)


class ListOrdenesUltimaSemanaTests(TestCase):
    @freeze_time('2024-01-15')
    def test_returns_impresas_closed_within_last_week(self):
        company = CompanyFactory()
        dentro = OrdenesDeTrabajoFactory(
            matafuegos__cliente__company=company, estado='i', fecha_cierre=date(2024, 1, 12),
        )
        OrdenesDeTrabajoFactory(
            matafuegos__cliente__company=company, estado='i', fecha_cierre=date(2024, 1, 15) - timedelta(days=10),
        )

        self.assertEqual(list(list_ordenes_ultima_semana(company)), [dentro])


class ListOrdenesRecargadasEntreTests(TestCase):
    def test_only_returns_ordenes_of_company(self):
        company = CompanyFactory()
        mia = OrdenesDeTrabajoFactory(
            matafuegos__cliente__company=company, estado='i', fecha_cierre=date(2024, 1, 10),
        )
        OrdenesDeTrabajoFactory(estado='i', fecha_cierre=date(2024, 1, 10))

        resultado = list_ordenes_recargadas_entre(company, '2024-01-01', '2024-01-31')

        self.assertEqual(list(resultado), [mia])

    def test_includes_impresas_and_facturadas_excludes_others(self):
        company = CompanyFactory()
        impresa = OrdenesDeTrabajoFactory(
            matafuegos__cliente__company=company, estado='i', fecha_cierre=date(2024, 1, 10),
        )
        facturada = OrdenesDeTrabajoFactory(
            matafuegos__cliente__company=company, estado='fac', fecha_cierre=date(2024, 1, 11),
        )
        OrdenesDeTrabajoFactory(
            matafuegos__cliente__company=company, estado='f', fecha_cierre=date(2024, 1, 12),
        )

        resultado = list_ordenes_recargadas_entre(company, '2024-01-01', '2024-01-31')

        self.assertEqual(set(resultado), {impresa, facturada})

    def test_excludes_ordenes_closed_outside_range(self):
        company = CompanyFactory()
        dentro = OrdenesDeTrabajoFactory(
            matafuegos__cliente__company=company, estado='i', fecha_cierre=date(2024, 1, 15),
        )
        OrdenesDeTrabajoFactory(
            matafuegos__cliente__company=company, estado='i', fecha_cierre=date(2024, 2, 1),
        )

        resultado = list_ordenes_recargadas_entre(company, '2024-01-01', '2024-01-31')

        self.assertEqual(list(resultado), [dentro])
