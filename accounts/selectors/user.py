from accounts.models import User


def list_usuarios(company):
    return User.objects.filter(company=company).order_by('username')
