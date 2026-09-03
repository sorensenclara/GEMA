from empresas.models import Company


def list_companies():
    return Company.objects.order_by('nombre')
