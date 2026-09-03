"""Renderizado de los informes en PDF a partir de templates Django, con
WeasyPrint, con estilos en CSS (ver reports/templates/reports/)."""

from django.template.loader import render_to_string
from weasyprint import HTML


def render_report_pdf(template_name, context):
    html = render_to_string(template_name, context)
    return HTML(string=html).write_pdf()
