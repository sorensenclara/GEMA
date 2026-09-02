from datetime import date
from .models import Matafuegos


def matafuegos_vencidos():
    matafuegos = Matafuegos.objects.all()
    for m in matafuegos:
        if m.fecha_fabricacion is not None:
            if (date.today() - m.fecha_fabricacion).days/365 > 21:
                m.vencido = True
                m.save()

