"""Emisión de las obleas DPS (vehicular y domiciliaria).

Migradas desde reportlab (dibujado a mano con canvas.drawString en puntos,
origen abajo-izquierda) a templates HTML + WeasyPrint. La conversión de
coordenadas es 1:1: reportlab mide en puntos (1/72") y CSS soporta la unidad
`pt` con la misma definición, así que cada `drawString(x, y, texto)` se
traduce en un `<span>` posicionado en `left: {x}pt; bottom: {y}pt;` dentro de
un contenedor del tamaño exacto de la página original (6.69291in x 12in) --
mismos números, sin redondeos ni reinterpretación de layout.

Estas obleas se imprimen sobre stock adhesivo físico con fines regulatorios
(DPS): antes de dar de baja el código reportlab, corresponde un control de
impresión física oblea-vieja vs. oblea-nueva sobre el mismo stock (ver plan
de migración) -- un defecto de alineación acá no es cosmético.
"""

from empresas.services import incrementar_dps
from orden_trabajo.exceptions import (
    CategoriaOrdenInvalidaException,
    OrdenNoFinalizadaException,
    OrdenSinFechaCierreException,
    OrdenSinTareaDeRecargaException,
)
from orden_trabajo.models import TareaOrden
from reports.services import render_report_pdf, resolve_company_name, resolve_numero_recargador

ANCHO_PAGINA = '6.69291in'
ALTO_PAGINA = '12in'
PT_POR_CM = 28.3465  # 1cm en puntos, para los ajustes finos de alineación de la oblea domiciliaria


def _actualizar_matafuego_y_marcar_impresa(orden, serie_dps):
    for tarea_orden in TareaOrden.objects.filter(orden=orden):
        if tarea_orden.tarea.es_recarga:
            orden.matafuegos.fecha_carga = orden.fecha_cierre
        if tarea_orden.tarea.nombre == 'Prueba Hidráulica':
            orden.matafuegos.fecha_ph = orden.fecha_cierre
    orden.matafuegos.numero_dps = incrementar_dps(orden.company, serie_dps)
    orden.matafuegos.save()
    orden.estado = 'i'
    orden.numero_dps = orden.matafuegos.numero_dps
    orden.save()


def _campo(texto, x, y, font_size=10):
    return {'texto': texto, 'x': x, 'y': y, 'font_size': font_size}


def _campos_oblea_vehicular(orden, x, y):
    m = orden.matafuegos
    campos = [
        _campo(str(m.numero), x + 3, y),
        _campo(str(m.fecha_fabricacion.year), x + 71, y),
    ]
    if m.fecha_proxima_ph:
        campos.append(_campo(f'{m.fecha_proxima_ph.month} {m.fecha_proxima_ph.year}', x + 110, y))
    campos += [
        _campo(str(m.tipo.volumen), x + 145, y),
        _campo(str(m.tipo), x + 176, y),
        _campo(resolve_company_name(orden), x + 3, y - 23),
        _campo(resolve_numero_recargador(orden), x + 128, y - 23),
        _campo(str(m.numero), x + 270, y - 22),
    ]
    if m.fecha_proxima_ph:
        campos.append(_campo(f'{m.fecha_proxima_ph.month} {m.fecha_proxima_ph.year}', x + 316, y - 22))
    if m.fecha_proxima_carga:
        campos += [
            _campo(str(m.fecha_proxima_carga.month), x + 8, y - 60),
            _campo(str(m.fecha_proxima_carga.year), x + 35, y - 60),
        ]
    campos.append(_campo(str(m.patente), x + 163, y - 60))
    if m.fecha_proxima_carga:
        campos += [
            _campo(str(m.fecha_proxima_carga.month), x + 264, y - 59),
            _campo(str(m.fecha_proxima_carga.year), x + 292, y - 58),
        ]
    campos.append(_campo(str(m.patente), x + 337, y - 60))
    campos.append(_campo(f'{resolve_company_name(orden)}  {resolve_numero_recargador(orden)}', x + 259, y - 89))
    return campos


def _paginas_oblea(ordenes, campos_fn, x_inicial, y_inicial, paso_y, x_reset, y_reset, paso_x=0):
    """Reproduce exactamente el loop original: dibuja cada orden en (x, y),
    baja `paso_y` puntos (y corre `paso_x` puntos en x), y cada 2 órdenes
    corta página reseteando la posición -- salvo tras el último par, que no
    corta (no hay más contenido)."""
    paginas = []
    campos_pagina = []
    x, y = x_inicial, y_inicial
    restantes = len(ordenes)
    for orden in ordenes:
        campos_pagina += campos_fn(orden, x, y)
        x += paso_x
        y -= paso_y
        restantes -= 1
        if restantes % 2 == 0 and restantes != 0:
            paginas.append(campos_pagina)
            campos_pagina = []
            x, y = x_reset, y_reset
    paginas.append(campos_pagina)
    return paginas


def emitir_oblea_vehicular(ordenes):
    ordenes = list(ordenes)
    for orden in ordenes:
        if orden.matafuegos.categoria not in ('v', 'ma'):
            raise CategoriaOrdenInvalidaException('Seleccionar solo categoria vehicular.')
    for orden in ordenes:
        if orden.estado not in ('f', 'i'):
            raise OrdenNoFinalizadaException(f'La orden N° {orden.id} no está finalizada.')
    for orden in ordenes:
        if not orden.fecha_cierre:
            raise OrdenSinFechaCierreException(f'La orden N° {orden.id} no tiene fecha de cierre: no se puede emitir la oblea.')
    for orden in ordenes:
        if not TareaOrden.objects.filter(orden=orden, tarea__es_recarga=True).exists():
            raise OrdenSinTareaDeRecargaException(f'La orden N° {orden.id} no tiene ninguna tarea de recarga: no se puede emitir la oblea.')

    for orden in ordenes:
        _actualizar_matafuego_y_marcar_impresa(orden, 'veh')

    paginas = _paginas_oblea(ordenes, _campos_oblea_vehicular, x_inicial=23, y_inicial=780, paso_y=280, x_reset=24, y_reset=786)
    return render_report_pdf('reports/oblea.html', {
        'paginas': paginas, 'ancho_pagina': ANCHO_PAGINA, 'alto_pagina': ALTO_PAGINA,
    })


def _campos_oblea_domiciliaria(orden, x, y):
    m = orden.matafuegos
    y_linea1 = y - 3 - 0.6 * PT_POR_CM
    y_linea2 = y - 26 - 0.7 * PT_POR_CM
    campos = [
        _campo(str(m.numero), x, y_linea1),
        _campo(str(m.fecha_fabricacion.year), x + 67, y_linea1),
        _campo(resolve_company_name(orden), x, y_linea2),
        _campo(resolve_numero_recargador(orden), x + 125, y_linea2),
    ]
    if m.fecha_proxima_ph:
        campos.append(_campo(f'{m.fecha_proxima_ph.month} {m.fecha_proxima_ph.year}', x + 105, y_linea1))
    campos += [
        _campo(str(m.tipo.volumen), x + 144, y_linea1),
        _campo(str(m.tipo), x + 173, y_linea1),
    ]
    if m.fecha_proxima_carga:
        campos += [
            _campo(str(m.fecha_proxima_carga.month), x + 8, y - 65 - 0.8 * PT_POR_CM),
            _campo(str(m.fecha_proxima_carga.year), x + 36, y - 65 - 0.8 * PT_POR_CM),
        ]

    nombre = str(orden.cliente.nombre)
    if len(nombre) > 22:
        ultimo_espacio = nombre.rfind(' ', 0, 21)
        if ultimo_espacio != -1:
            primera_parte, segunda_parte = nombre[:ultimo_espacio], nombre[ultimo_espacio + 1:]
        else:
            primera_parte, segunda_parte = nombre[:22], nombre[22:]
        campos.append(_campo(primera_parte, x + 73 + 0.2 * PT_POR_CM, y - 54 - 0.6 * PT_POR_CM, font_size=7))
        campos.append(_campo(segunda_parte, x + 73 + 0.2 * PT_POR_CM, y - 64 - 0.6 * PT_POR_CM, font_size=7))
    else:
        campos.append(_campo(nombre, x + 73 + 0.2 * PT_POR_CM, y - 54 - 0.6 * PT_POR_CM, font_size=7))

    campos.append(_campo(str(m.numero), x + 254 + 0.4 * PT_POR_CM, y - 28 - 0.5 * PT_POR_CM))
    if m.fecha_proxima_ph:
        campos.append(_campo(f'{m.fecha_proxima_ph.month} {m.fecha_proxima_ph.year}', x + 312 + 0.4 * PT_POR_CM, y - 28 - 0.5 * PT_POR_CM))
    if m.fecha_proxima_carga:
        campos += [
            _campo(str(m.fecha_proxima_carga.month), x + 256 + 0.5 * PT_POR_CM, y - 64 - 0.7 * PT_POR_CM),
            _campo(str(m.fecha_proxima_carga.year), x + 286 + 0.5 * PT_POR_CM, y - 64 - 0.7 * PT_POR_CM),
        ]
    campos.append(_campo(f'{resolve_company_name(orden)}  {resolve_numero_recargador(orden)}', x + 269 + 0.5 * PT_POR_CM, y - 90 - 0.5 * PT_POR_CM))
    return campos


def emitir_oblea_domiciliaria(ordenes):
    ordenes = list(ordenes)
    for orden in ordenes:
        if orden.estado not in ('f', 'i'):
            raise OrdenNoFinalizadaException(f'La orden N° {orden.id} no está finalizada.')
    for orden in ordenes:
        if not orden.fecha_cierre:
            raise OrdenSinFechaCierreException(f'La orden N° {orden.id} no tiene fecha de cierre: no se puede emitir la oblea.')
    for orden in ordenes:
        if orden.matafuegos.categoria != 'd':
            raise CategoriaOrdenInvalidaException('Seleccionar solo categoria domiciliaria.')
    for orden in ordenes:
        if not TareaOrden.objects.filter(orden=orden, tarea__es_recarga=True).exists():
            raise OrdenSinTareaDeRecargaException(f'La orden N° {orden.id} no tiene ninguna tarea de recarga: no se puede emitir la oblea.')

    for orden in ordenes:
        _actualizar_matafuego_y_marcar_impresa(orden, 'dom')

    paginas = _paginas_oblea(
        ordenes, _campos_oblea_domiciliaria,
        x_inicial=20.50, y_inicial=809.84, paso_y=295.34, paso_x=2.83,
        x_reset=20.50, y_reset=810.84,
    )
    return render_report_pdf('reports/oblea.html', {
        'paginas': paginas, 'ancho_pagina': ANCHO_PAGINA, 'alto_pagina': ALTO_PAGINA,
    })
