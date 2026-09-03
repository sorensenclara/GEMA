from orden_trabajo.models import Tarea


def list_tareas(company):
    return Tarea.objects.filter(company=company).order_by('nombre')
