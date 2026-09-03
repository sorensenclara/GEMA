from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404
from django.shortcuts import get_object_or_404, render
from django.utils.http import url_has_allowed_host_and_scheme
from django.views import View

from core.selectors import attach_diffs, list_history_for_object, resolve_history_model
from core.utils import paginate, resolve_company


class HistoryView(LoginRequiredMixin, View):
    """
    Generic, read-only change history for any model based on AuditModel.
    Never implemented per-app -- every entity's "Historial" button links here.

    Scoped by compañía: un usuario no-superuser solo puede ver el historial
    de objetos de su propia compañía (resuelta vía `resolve_company`, la
    misma lógica que ya usan los informes en PDF para encontrar el tenant
    de un objeto sin atarse a una ruta de FK exacta).
    """
    template_name = "core/history.html"

    def get(self, request, app_label, model_name, pk):
        model = resolve_history_model(app_label, model_name)
        if model is None:
            raise Http404("Modelo no encontrado o sin historial habilitado")

        obj = get_object_or_404(model, pk=pk)
        if not request.user.is_superuser:
            company = resolve_company(obj)
            if company is None or company.pk != request.user.company_id:
                raise Http404("Modelo no encontrado o sin historial habilitado")
        history = list_history_for_object(obj)
        page = paginate(history, request)
        attach_diffs(page.object_list)

        return render(request, self.template_name, {
            "object": obj,
            "object_name": model._meta.verbose_name,
            "page_obj": page,
            "page_title": f"Historial de {model._meta.verbose_name}: {obj}",
            "back_url": self._get_back_url(request),
            "list_url": self._get_safe_url(request, "list_url"),
            "list_label": request.GET.get("list_label", ""),
        })

    def _get_safe_url(self, request, param):
        url = request.GET.get(param)
        if url and url_has_allowed_host_and_scheme(url, allowed_hosts={request.get_host()}, require_https=request.is_secure()):
            return url
        return None

    def _get_back_url(self, request):
        next_url = self._get_safe_url(request, "next")
        if next_url:
            return next_url

        referer = request.META.get("HTTP_REFERER")
        if referer and url_has_allowed_host_and_scheme(referer, allowed_hosts={request.get_host()}, require_https=request.is_secure()):
            return referer

        return None
