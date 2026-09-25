from unittest.mock import Mock, patch

from django.core.cache import cache
from django.test import SimpleTestCase

from core.services.geocoding import GeocodingError, buscar_ubicaciones, obtener_seleccion

RESULTADO_NOMINATIM_SAN_CAYETANO = [
    {
        'place_id': 999999,  # a propósito no se usa: ver test de geo_referencia_externa
        'osm_type': 'way',
        'osm_id': 123456789,
        'display_name': 'Av. San Martín 450, San Cayetano, Buenos Aires, Argentina',
        'address': {
            'road': 'Av. San Martín',
            'house_number': '450',
            'town': 'San Cayetano',
            'state': 'Buenos Aires',
            'postcode': '7609',
            'country': 'Argentina',
            'country_code': 'ar',
        },
    },
]


class BuscarUbicacionesTests(SimpleTestCase):
    def setUp(self):
        cache.clear()

    def test_texto_vacio_no_llama_a_nominatim(self):
        with patch('core.services.geocoding.requests.get') as mock_get:
            self.assertEqual(buscar_ubicaciones('   '), [])
            mock_get.assert_not_called()

    @patch('core.services.geocoding._throttle')
    @patch('core.services.geocoding.requests.get')
    def test_normaliza_el_resultado_y_usa_osm_type_osm_id_como_referencia(self, mock_get, mock_throttle):
        mock_get.return_value = Mock(json=lambda: RESULTADO_NOMINATIM_SAN_CAYETANO, raise_for_status=lambda: None)

        sugerencias = buscar_ubicaciones('San Martin 450 San Cayetano')

        self.assertEqual(len(sugerencias), 1)
        self.assertEqual(sugerencias[0]['direccion'], 'Av. San Martín 450, San Cayetano, Buenos Aires, Argentina')
        seleccion = obtener_seleccion(sugerencias[0]['token'])
        self.assertEqual(seleccion['localidad'], 'San Cayetano')
        self.assertEqual(seleccion['provincia'], 'Buenos Aires')
        self.assertEqual(seleccion['codigo_postal'], '7609')
        self.assertEqual(seleccion['pais'], 'Argentina')
        # osm_type:osm_id, nunca el place_id (ver docstring de core/services/geocoding.py).
        self.assertEqual(seleccion['geo_referencia_externa'], 'way:123456789')

    @patch('core.services.geocoding._throttle')
    @patch('core.services.geocoding.requests.get')
    def test_segunda_busqueda_identica_no_vuelve_a_llamar_a_nominatim(self, mock_get, mock_throttle):
        mock_get.return_value = Mock(json=lambda: RESULTADO_NOMINATIM_SAN_CAYETANO, raise_for_status=lambda: None)

        buscar_ubicaciones('San Martin 450 San Cayetano')
        buscar_ubicaciones('San Martin 450 San Cayetano')

        self.assertEqual(mock_get.call_count, 1)

    @patch('core.services.geocoding._throttle')
    @patch('core.services.geocoding.requests.get')
    def test_localidad_cae_a_city_town_village_hamlet_suburb_en_ese_orden(self, mock_get, mock_throttle):
        resultado = [{
            'osm_type': 'node', 'osm_id': 1, 'display_name': 'x',
            'address': {'village': 'Un Paraje Rural', 'state': 'Buenos Aires'},
        }]
        mock_get.return_value = Mock(json=lambda: resultado, raise_for_status=lambda: None)

        sugerencias = buscar_ubicaciones('paraje rural')
        seleccion = obtener_seleccion(sugerencias[0]['token'])
        self.assertEqual(seleccion['localidad'], 'Un Paraje Rural')

    @patch('core.services.geocoding._throttle')
    @patch('core.services.geocoding.requests.get')
    def test_sin_resultados_devuelve_lista_vacia(self, mock_get, mock_throttle):
        mock_get.return_value = Mock(json=lambda: [], raise_for_status=lambda: None)
        self.assertEqual(buscar_ubicaciones('direccion que no existe'), [])

    @patch('core.services.geocoding._throttle')
    @patch('core.services.geocoding.requests.get')
    def test_error_de_transporte_levanta_geocoding_error(self, mock_get, mock_throttle):
        import requests
        mock_get.side_effect = requests.ConnectionError('sin red')
        with self.assertRaises(GeocodingError):
            buscar_ubicaciones('cualquier cosa')


class ObtenerSeleccionTests(SimpleTestCase):
    def setUp(self):
        cache.clear()

    def test_token_inexistente_devuelve_none(self):
        self.assertIsNone(obtener_seleccion('token-que-nunca-existio'))

    def test_token_vacio_devuelve_none(self):
        self.assertIsNone(obtener_seleccion(''))
        self.assertIsNone(obtener_seleccion(None))
