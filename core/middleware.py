import threading

_thread_locals = threading.local()


def get_current_user():
    return getattr(_thread_locals, 'user', None)


class CurrentUserMiddleware:
    """Exposes the request's user via a thread-local so AuditModel.save()
    can fill created_by/updated_by without needing `request` passed down
    into services/models."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        _thread_locals.user = getattr(request, 'user', None)
        response = self.get_response(request)
        if hasattr(_thread_locals, 'user'):
            del _thread_locals.user
        return response
