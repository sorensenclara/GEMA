"""Paleta y helpers de marca compartidos por los informes en PDF y por el
theme del admin (reports/fixtures/export_interface.json, cuyos valores hex
deben mantenerse en sintonía con esta paleta a mano, ya que un fixture JSON
no puede importar estas constantes)."""

import os
import pathlib

from core.utils import resolve_company

# Paleta extraída de https://gema.geneos.com.ar/style.css
GEMA_NAVY = "#1B4B8D"
GEMA_WHITE = "#FFFFFF"
GEMA_DARK_TEXT = "#232323"
GEMA_PASTEL_BG = "#EDF5FF"
GEMA_PASTEL_BG_ALT = "#C1EDFE"
GEMA_CYAN = "#4AC5F3"
GEMA_ORANGE = "#EC6C05"

DEFAULT_COMPANY_NAME = "GEMA"
DEFAULT_NUMERO_RECARGADOR = "120"
# reports/assets/, no reports/services/assets/ -- un nivel arriba del propio
# archivo (reports/services/branding.py).
DEFAULT_LOGO_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "gema-logo.png")


def resolve_company_name(obj):
    company = resolve_company(obj)
    if company and getattr(company, "nombre", None):
        return company.nombre
    return DEFAULT_COMPANY_NAME


def resolve_numero_recargador(obj):
    company = resolve_company(obj)
    if company and getattr(company, "numero_recargador", None):
        return company.numero_recargador
    return DEFAULT_NUMERO_RECARGADOR


def resolve_logo_path(obj):
    """Devuelve la ruta de archivo del logo en disco. Si la compañía tiene
    logo propio cargado, devuelve la ruta a ese archivo; si no, cae al logo
    genérico de GEMA. Usado por `resolve_logo_uri` para armar el `file://`
    que consumen los templates renderizados con WeasyPrint."""
    company = resolve_company(obj)
    if company and getattr(company, "logo", None):
        try:
            if company.logo and os.path.exists(company.logo.path):
                return company.logo.path
        except (ValueError, NotImplementedError):
            pass
    return DEFAULT_LOGO_PATH


def resolve_logo_uri(obj):
    """Devuelve la ruta de `resolve_logo_path` como URI `file://`, utilizable
    directo en un `<img src>` de un template renderizado con WeasyPrint."""
    return pathlib.Path(resolve_logo_path(obj)).as_uri()


def report_header_context(obj, titulo):
    """Contexto compartido por los templates de informes en
    `reports/templates/reports/`, para el bloque de encabezado de `_base.html`."""
    return {
        'titulo': titulo,
        'logo_uri': resolve_logo_uri(obj),
        'empresa': resolve_company_name(obj) if obj is not None else DEFAULT_COMPANY_NAME,
    }
