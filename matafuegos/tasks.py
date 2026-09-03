"""Wrapper fino para django-crontab (ver settings.CRONJOBS) -- la lógica de
negocio vive en matafuegos/services/matafuegos.py::marcar_vencidos(), testeable
sin depender del cron."""

from matafuegos.services import marcar_vencidos


def matafuegos_vencidos():
    marcar_vencidos()
