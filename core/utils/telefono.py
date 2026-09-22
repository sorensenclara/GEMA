"""Utilidades para dejar los telefonos de contacto en formato internacional
listo para WhatsApp (54 9 + numero significativo nacional de 10 digitos).

Pensado inicialmente para Cliente.telefono (ver charla con Clara,
2026-09-22: "podria hacer que siempre sea apto para whatsapp?"), pero vive
en core/utils porque no hay nada especifico de "cliente" en la logica --
cualquier otro modelo que guarde un telefono argentino puede reutilizarla.

Reglas de Argentina que aplica:
  - El numero significativo nacional (NSN) siempre tiene 10 digitos
    (codigo de area + abonado), sin importar que el codigo de area tenga
    2, 3 o 4 digitos -- por eso alcanza con la longitud y NO hace falta
    (ni existe aca) una tabla de codigos de area.
  - En formato de discado local se antepone un "0" (prefijo de larga
    distancia) y, para celulares, se inserta un "15" justo despues del
    codigo de area y antes del abonado.
  - En formato internacional para WhatsApp el "0" y el "15" se sacan, y en
    su lugar va "54" (pais) + "9" (marca de celular) + el NSN de 10
    digitos: 54 9 <NSN> = 13 digitos en total.
"""

import re

PREFIJO_PAIS = '54'
MARCA_CELULAR = '9'
LARGO_NSN = 10


class TelefonoInvalidoException(Exception):
    """El telefono no tiene una cantidad de digitos reconocible como un
    numero argentino (fijo u orden de discado celular con "15") y no se
    pudo normalizar de forma confiable a formato internacional."""


def _quitar_marcador_15(digitos):
    """`digitos` es la cadena de 12 digitos que queda luego de sacar el "0"
    inicial de un numero celular en formato de discado local (codigo de
    area + "15" + abonado). Busca el "15" en las posiciones donde puede
    estar segun el largo posible del codigo de area (2, 3 o 4 digitos) y
    devuelve el NSN de 10 digitos con el "15" ya removido. Si no encuentra
    un "15" en ninguna posicion candidata, devuelve None (no se pudo
    resolver sin una tabla de codigos de area)."""
    if digitos[:2] == '11' and digitos[2:4] == '15':
        # Unico codigo de area de 2 digitos (CABA/GBA) -- lo resolvemos
        # primero para no depender del orden en que probamos los largos.
        return digitos[:2] + digitos[4:]
    for largo_area in (3, 4, 2):
        if digitos[largo_area:largo_area + 2] == '15':
            return digitos[:largo_area] + digitos[largo_area + 2:]
    return None


def normalizar_telefono_ar(valor):
    """Normaliza un telefono argentino a formato internacional listo para
    WhatsApp: "549" + 10 digitos (sin espacios, guiones ni "+").

    Devuelve None si `valor` viene vacio (no es un error -- el campo es
    opcional). Es idempotente: normalizar un numero ya normalizado devuelve
    el mismo valor. Levanta TelefonoInvalidoException si no se puede
    reconocer con confianza como un numero argentino."""
    if not valor or not valor.strip():
        return None

    digitos = re.sub(r'\D', '', valor)
    if not digitos:
        raise TelefonoInvalidoException(
            f'"{valor}" no tiene ningun digito -- no se puede normalizar.'
        )

    resto = digitos
    if resto.startswith(PREFIJO_PAIS):
        resto = resto[len(PREFIJO_PAIS):]
        if resto.startswith(MARCA_CELULAR):
            resto = resto[len(MARCA_CELULAR):]

    if resto.startswith('0'):
        resto = resto[1:]

    if len(resto) == LARGO_NSN + 2:
        nsn = _quitar_marcador_15(resto)
        if nsn is None:
            raise TelefonoInvalidoException(
                f'"{valor}" tiene {len(resto)} digitos en la parte nacional, pero no '
                'se pudo ubicar el marcador "15" de celular -- revisar a mano.'
            )
    else:
        nsn = resto

    if len(nsn) != LARGO_NSN:
        raise TelefonoInvalidoException(
            f'"{valor}" tiene {len(nsn)} digitos en la parte nacional (deberian ser '
            f'{LARGO_NSN}) -- no se puede normalizar con confianza.'
        )

    return f'{PREFIJO_PAIS}{MARCA_CELULAR}{nsn}'


def es_telefono_normalizado(valor):
    """True si `valor` ya esta en formato internacional listo para
    WhatsApp (549 + 10 digitos, sin ningun otro caracter)."""
    return bool(valor) and bool(re.fullmatch(r'549\d{10}', valor))


def whatsapp_url(valor):
    """URL de wa.me para abrir un chat directo con ese numero, o None si
    `valor` no esta en formato internacional (deberia estarlo siempre
    luego de guardar un Cliente, pero por las dudas frente a datos
    historicos todavia sin migrar)."""
    if not es_telefono_normalizado(valor):
        return None
    return f'https://wa.me/{valor}'
