from .branding import (
    report_header_context,
    resolve_company,
    resolve_company_name,
    resolve_logo_path,
    resolve_logo_uri,
    resolve_numero_recargador,
)
from .pdf_render import render_report_pdf

__all__ = [
    'render_report_pdf',
    'report_header_context',
    'resolve_company',
    'resolve_company_name',
    'resolve_logo_path',
    'resolve_logo_uri',
    'resolve_numero_recargador',
]
