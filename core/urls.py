from django.urls import path

from . import views

app_name = "core"

urlpatterns = [
    path(
        "history/<str:app_label>/<str:model_name>/<int:pk>/",
        views.HistoryView.as_view(),
        name="history",
    ),
]
