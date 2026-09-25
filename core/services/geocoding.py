"""Capa de abstracción para búsqueda de ubicaciones / geocodificación.

Hoy está implementada sobre el servidor público de Nominatim (proyecto
OpenStreetMap), respetando su política de uso oficial
(https://operations.osmfoundation.org/policies/nominatim/):
  - Sin autocomplete por tecla: solo se consulta cuando el usuario dispara
    una búsqueda explícita (botón "Buscar" o Enter).
  - User-Agent identificando a la aplicación (exigido por la política).
  - Caché de resultados repetidos (misma búsqueda no vuelve a golpear a
    Nominatim).
  - Throttle a un máximo de ~1 request/segundo hacia Nominatim, sumando
    TODO el tráfico de GEMA (todas las empresas), tal como lo exige la
    política ("the sum of traffic by all your users should not exceed
    the limits").
  - Sin geocodificación masiva: esto solo se llama cuando un usuario busca
    una dirección puntual desde el formulario de Cliente.

El resto de GEMA (forms, views, templates) NO debe importar `requests` ni
conocer nada de Nominatim: solo debe llamar a `buscar_ubicaciones()` y a
`obtener_seleccion()`, que devuelven/reciben una estructura normalizada
propia de GEMA (ver `_normalizar`). Si el día de mañana cambiamos de
proveedor -- por ejemplo porque el volumen de GEMA supera lo razonable
para el servidor público de Nominatim -- alcanza con reescribir este
archivo; Cliente no necesita cambiar.

LIMITACIÓN CONOCIDA (multi-proceso): el throttle y la caché de búsquedas
usan el cache framework de Django (`django.core.cache`). Como el proyecto
no tiene configurado `CACHES` en `gema/settings.py`, Django usa por
defecto `LocMemCache`, que es memoria LOCAL DE CADA PROCESO. Mientras GEMA
corra en un solo proceso esto alcanza. Si en producción se pasa a correr
con varios workers (Gunicorn con `--workers > 1`, por ejemplo), cada
proceso cuenta su propio "último request" por separado, y el límite real
de 1 req/seg del servidor público podría superarse levemente en la
práctica. El día que eso ocurra, hay que configurar un backend de caché
compartido (Redis/Memcached) en `CACHES` -- no hace falta tocar este
archivo ni ningún otro.
"""
import hashlib
import time
import uuid

import requests
from django.core.cache import cache

NOMINATIM_URL = 'https://nominatim.openstreetmap.org/search'

# Identificación de la aplicación exigida por la política de uso de
# Nominatim ("stock User-Agents as set by http libraries will not do").
USER_AGENT = 'GEMA-GENEOS/1.0 (+https://gema.geneos.com.ar; contacto: contacto@geneos.com.ar)'

TIMEOUT_SEGUNDOS = 5
LIMITE_RESULTADOS = 5

# Cuánto tiempo se recuerda una búsqueda ya hecha, para no repetirla ante
# el mismo texto (parte de "results must be cached" en la política de uso).
TTL_CACHE_BUSQUEDA = 60 * 60 * 24  # 24 horas

# Cuánto tiempo queda disponible una sugerencia concreta para ser
# seleccionada y guardada en el formulario de Cliente.
TTL_CACHE_SELECCION = 60 * 15  # 15 minutos

THROTTLE_CACHE_KEY = 'geocoding:nominatim:ultimo_request'
THROTTLE_SEGUNDOS = 1.1  # margen sobre el 1 req/seg exigido por la política


class GeocodingError(Exception):
    """Nominatim no respondió o respondió con un error de transporte.

    El llamador debe tratar esto igual que "sin resultados" -- nunca debe
    impedir que se cree o edite un Cliente porque el proveedor de
    geocodificación falle."""


def _throttle():
    """Espera lo necesario para no superar ~1 request/segundo hacia
    Nominatim. Ver la limitación de multi-proceso en el docstring del
    módulo: esto es por-proceso, no un límite global estricto."""
    ultimo = cache.get(THROTTLE_CACHE_KEY)
    ahora = time.monotonic()
    if ultimo is not None:
        espera = THROTTLE_SEGUNDOS - (ahora - ultimo)
        if espera > 0:
            time.sleep(espera)
    cache.set(THROTTLE_CACHE_KEY, time.monotonic(), timeout=THROTTLE_SEGUNDOS + 1)


def _mejor_localidad(address):
    """Nominatim devuelve la localidad bajo distintas claves según el tipo
    de asentamiento; se toma la primera que venga con datos."""
    for clave in ('city', 'town', 'village', 'hamlet', 'suburb'):
        if address.get(clave):
            return address[clave]
    return ''


def _normalizar(item):
    """Convierte un resultado crudo de Nominatim a la estructura propia de
    GEMA. Los `[:N]` son un resguardo defensivo por si Nominatim devolviera
    un texto más largo que el max_length de los campos de Cliente."""
    address = item.get('address', {})
    return {
        'direccion': (item.get('display_name') or '')[:255],
        'localidad': _mejor_localidad(address)[:120],
        'provincia': (address.get('state') or '')[:120],
        'codigo_postal': (address.get('postcode') or '')[:20],
        'pais': (address.get('country') or '')[:80],
        # Nominatim documenta su propio "place_id" como interno y NO
        # estable entre instalaciones/actualizaciones de su base; el
        # identificador que ellos recomiendan para uso externo es la
        # combinación osm_type + osm_id.
        'geo_referencia_externa': f"{item.get('osm_type', '')}:{item.get('osm_id', '')}"[:50],
    }


def buscar_ubicaciones(texto, pais='ar', limite=LIMITE_RESULTADOS):
    """Busca `texto` como una dirección real usando Nominatim.

    Devuelve una lista de hasta `limite` dicts {"token": str, "direccion":
    str} listos para mostrarle al usuario como opciones para elegir. Nunca
    lanza una excepción por "sin resultados" (devuelve lista vacía); puede
    lanzar `GeocodingError` si el proveedor no responde, para que la vista
    lo trate igual que "sin resultados" de cara al usuario."""
    texto = (texto or '').strip()
    if not texto:
        return []

    # Se hashea el texto en la clave de cache (en vez de usarlo tal cual)
    # para que la clave sea valida tambien si el dia de manana se pasa a
    # un backend de cache tipo Memcached, que no acepta espacios/caracteres
    # de control en las keys.
    texto_hash = hashlib.sha1(texto.lower().encode('utf-8')).hexdigest()
    cache_key = f'geocoding:nominatim:busqueda:{pais}:{texto_hash}'
    resultados_crudos = cache.get(cache_key)
    if resultados_crudos is None:
        _throttle()
        try:
            respuesta = requests.get(
                NOMINATIM_URL,
                params={
                    'q': texto,
                    'format': 'jsonv2',
                    'addressdetails': 1,
                    'countrycodes': pais,
                    'limit': limite,
                },
                headers={'User-Agent': USER_AGENT},
                timeout=TIMEOUT_SEGUNDOS,
            )
            respuesta.raise_for_status()
            resultados_crudos = respuesta.json()
        except (requests.RequestException, ValueError) as exc:
            raise GeocodingError(str(exc)) from exc
        cache.set(cache_key, resultados_crudos, timeout=TTL_CACHE_BUSQUEDA)

    sugerencias = []
    for item in resultados_crudos[:limite]:
        normalizado = _normalizar(item)
        token = uuid.uuid4().hex
        cache.set(f'geocoding:seleccion:{token}', normalizado, timeout=TTL_CACHE_SELECCION)
        sugerencias.append({'token': token, 'direccion': normalizado['direccion']})
    return sugerencias


def obtener_seleccion(token):
    """Devuelve el dict normalizado guardado para `token` por una búsqueda
    reciente (ver `buscar_ubicaciones`), o None si el token no existe,
    venció, o nunca existió (por ejemplo, alguien lo escribió a mano)."""
    if not token:
        return None
    return cache.get(f'geocoding:seleccion:{token}')
