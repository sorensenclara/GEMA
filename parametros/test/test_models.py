from django.core.exceptions import ValidationError
from django.test import TestCase
from parametros.models import Parametros

class YourTestClass(TestCase):

    @classmethod
    def setUpTestData(cls):
        #print("setUpTestData: Run once to set up non-modified data for all class methods.")
        parametros = Parametros.objects.create(veh_inicio=1,
                                                veh_fin=2,
                                                veh_prefijo='3',
                                                veh_actual=4,
                                                dom_inicio=5,
                                                dom_fin=6,
                                                dom_prefijo='7',
                                                dom_actual=8)

        pass

    # ETIQUETAS ------------------------------------------------------------------------------------------------

    def test_veh_inicio_label(self):
        parametros = Parametros.objects.get(id=1)
        field_label = parametros._meta.get_field('veh_inicio').verbose_name
        self.assertEquals(field_label,'VEH inicio')

    def test_veh_fin_label(self):
        parametros = Parametros.objects.get(id=1)
        field_label = parametros._meta.get_field('veh_fin').verbose_name
        self.assertEquals(field_label,'VEH fin')

    def test_veh_prefijo_label(self):
        parametros = Parametros.objects.get(id=1)
        field_label = parametros._meta.get_field('veh_prefijo').verbose_name
        self.assertEquals(field_label,'VEH prefijo')

    def test_veh_actual_label(self):
        parametros = Parametros.objects.get(id=1)
        field_label = parametros._meta.get_field('veh_actual').verbose_name
        self.assertEquals(field_label,'VEH actual')

    def test_dom_inicio_label(self):
        parametros = Parametros.objects.get(id=1)
        field_label = parametros._meta.get_field('dom_inicio').verbose_name
        self.assertEquals(field_label,'DOM inicio')

    def test_dom_fin_label(self):
        parametros = Parametros.objects.get(id=1)
        field_label = parametros._meta.get_field('dom_fin').verbose_name
        self.assertEquals(field_label,'DOM fin')

    def test_dom_prefijo_label(self):
        parametros = Parametros.objects.get(id=1)
        field_label = parametros._meta.get_field('dom_prefijo').verbose_name
        self.assertEquals(field_label,'DOM prefijo')

    def test_dom_actual_label(self):
        parametros = Parametros.objects.get(id=1)
        field_label = parametros._meta.get_field('dom_actual').verbose_name
        self.assertEquals(field_label,'DOM actual')

    def test_email_label(self):
        parametros = Parametros.objects.get(id=1)
        field_label = parametros._meta.get_field('email').verbose_name
        self.assertEquals(field_label,'Email')

    def test_contraseña_label(self):
        parametros = Parametros.objects.get(id=1)
        field_label = parametros._meta.get_field('password').verbose_name
        self.assertEquals(field_label,'Contraseña')

    # LONGITUD -------------------------------------------------------------------------------------------------

    def test_veh_prefijo_length(self):
        parametros = Parametros.objects.get(id=1)
        max_length = parametros._meta.get_field('veh_prefijo').max_length
        self.assertEquals(max_length,5)

    def test_dom_prefijo_length(self):
        parametros = Parametros.objects.get(id=1)
        max_length = parametros._meta.get_field('dom_prefijo').max_length
        self.assertEquals(max_length,5)

    def test_email_length(self):
        parametros = Parametros.objects.get(id=1)
        max_length = parametros._meta.get_field('email').max_length
        self.assertEquals(max_length,264)

    def test_dom_contraseña_length(self):
        parametros = Parametros.objects.get(id=1)
        max_length = parametros._meta.get_field('password').max_length
        self.assertEquals(max_length,20)

    #if self.veh_inicio<0:
    #    raise ValidationError('El VEH inicio debe ser mayor o igual a 0')
    def test_veh_inicio(self):
        parametros = Parametros.objects.create(veh_inicio=-1,
                                                veh_fin=2,
                                                veh_prefijo='3',
                                                veh_actual=4,
                                                dom_inicio=5,
                                                dom_fin=6,
                                                dom_prefijo='7',
                                                dom_actual=8)
        with self.assertRaises(ValidationError) as e:
            parametros.clean()
        self.assertEqual("['El VEH inicio debe ser mayor o igual a 0']",str(e.exception))

    #if self.veh_fin<0:
    #    raise ValidationError('El VEH fin debe ser mayor o igual a 0')
    def test_veh_fin(self):
        parametros = Parametros.objects.create(veh_inicio=1,
                                                veh_fin=-2,
                                                veh_prefijo='3',
                                                veh_actual=4,
                                                dom_inicio=5,
                                                dom_fin=6,
                                                dom_prefijo='7',
                                                dom_actual=8)
        with self.assertRaises(ValidationError) as e:
            parametros.clean()
        self.assertEqual("['El VEH fin debe ser mayor o igual a 0']",str(e.exception))

    #if self.veh_actual<0:
    #    raise ValidationError('El VEH actual debe ser mayor o igual a 0')
    def test_veh_actual(self):
        parametros = Parametros.objects.create(veh_inicio=1,
                                                veh_fin=2,
                                                veh_prefijo='3',
                                                veh_actual=-4,
                                                dom_inicio=5,
                                                dom_fin=6,
                                                dom_prefijo='7',
                                                dom_actual=8)
        with self.assertRaises(ValidationError) as e:
            parametros.clean()
        self.assertEqual("['El VEH actual debe ser mayor o igual a 0']",str(e.exception))

    #if self.veh_actual<self.veh_inicio:
    #    raise ValidationError('El VEH actual debe ser mayor o igual al VEH inicio')
    def test_veh_actual_inicio(self):
        parametros = Parametros.objects.create(veh_inicio=1,
                                                veh_fin=2,
                                                veh_prefijo='3',
                                                veh_actual=0,
                                                dom_inicio=5,
                                                dom_fin=6,
                                                dom_prefijo='7',
                                                dom_actual=8)
        with self.assertRaises(ValidationError) as e:
            parametros.clean()
        self.assertEqual("['El VEH actual debe ser mayor o igual al VEH inicio']",str(e.exception))

    #if self.veh_actual>self.veh_fin:
    #    raise ValidationError('El VEH actual debe ser menor o igual al VEH fin')
    def test_veh_actual_fin(self):
        parametros = Parametros.objects.create(veh_inicio=1,
                                                veh_fin=2,
                                                veh_prefijo='3',
                                                veh_actual=3,
                                                dom_inicio=5,
                                                dom_fin=6,
                                                dom_prefijo='7',
                                                dom_actual=8)
        with self.assertRaises(ValidationError) as e:
            parametros.clean()
        self.assertEqual("['El VEH actual debe ser menor o igual al VEH fin']",str(e.exception))

    #if self.dom_inicio<0:
    #    raise ValidationError('El DOM inicio debe ser mayor o igual a 0')
    def test_dom_inicio(self):
        parametros = Parametros.objects.create(veh_inicio=1,
                                                veh_fin=2,
                                                veh_prefijo='3',
                                                veh_actual=2,
                                                dom_inicio=-5,
                                                dom_fin=6,
                                                dom_prefijo='7',
                                                dom_actual=8)
        with self.assertRaises(ValidationError) as e:
            parametros.clean()
        self.assertEqual("['El DOM inicio debe ser mayor o igual a 0']",str(e.exception))

    #if self.dom_fin<0:
    #    raise ValidationError('El DOM fin debe ser mayor o igual a 0')
    def test_dom_fin(self):
        parametros = Parametros.objects.create(veh_inicio=1,
                                                veh_fin=2,
                                                veh_prefijo='3',
                                                veh_actual=2,
                                                dom_inicio=5,
                                                dom_fin=-6,
                                                dom_prefijo='7',
                                                dom_actual=8)
        with self.assertRaises(ValidationError) as e:
            parametros.clean()
        self.assertEqual("['El DOM fin debe ser mayor o igual a 0']",str(e.exception))

    #if self.dom_actual<0:
    #    raise ValidationError('El DOM actual debe ser mayor o igual a 0')
    def test_dom_actual(self):
        parametros = Parametros.objects.create(veh_inicio=1,
                                                veh_fin=2,
                                                veh_prefijo='3',
                                                veh_actual=2,
                                                dom_inicio=5,
                                                dom_fin=6,
                                                dom_prefijo='7',
                                                dom_actual=-8)
        with self.assertRaises(ValidationError) as e:
            parametros.clean()
        self.assertEqual("['El DOM actual debe ser mayor o igual a 0']",str(e.exception))

    #if self.dom_actual<self.dom_inicio:
    #    raise ValidationError('El DOM actual debe ser mayor o igual al DOM inicio')
    def test_dom_actual_inicio(self):
        parametros = Parametros.objects.create(veh_inicio=1,
                                                veh_fin=2,
                                                veh_prefijo='3',
                                                veh_actual=2,
                                                dom_inicio=5,
                                                dom_fin=6,
                                                dom_prefijo='7',
                                                dom_actual=4)
        with self.assertRaises(ValidationError) as e:
            parametros.clean()
        self.assertEqual("['El DOM actual debe ser mayor o igual al DOM inicio']",str(e.exception))

    #if self.dom_actual>self.dom_fin:
    #    raise ValidationError('El DOM actual debe ser menor o igual al DOM fin')
    def test_dom_actual_fin(self):
        parametros = Parametros.objects.create(veh_inicio=1,
                                                veh_fin=2,
                                                veh_prefijo='3',
                                                veh_actual=2,
                                                dom_inicio=5,
                                                dom_fin=6,
                                                dom_prefijo='7',
                                                dom_actual=7)
        with self.assertRaises(ValidationError) as e:
            parametros.clean()
        self.assertEqual("['El DOM actual debe ser menor o igual al DOM fin']",str(e.exception))

"""
    def setUp(self):
        print("setUp: Run once for every test method to setup clean data.")
        pass
    def test_false_is_false(self):
        print("Method: test_false_is_false.")
        self.assertFalse(False)

    def test_false_is_true(self):
        print("Method: test_false_is_true.")
        self.assertTrue(False)

    def test_one_plus_one_equals_two(self):
        print("Method: test_one_plus_one_equals_two.")
        self.assertEqual(1 + 1, 2)
"""
