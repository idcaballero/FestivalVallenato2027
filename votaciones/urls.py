from django.urls import path
from . import views

app_name = "votaciones"

urlpatterns = [
    path("", views.inicio, name="inicio"),
    path("categorias/", views.categorias, name="categorias"),
    path(
        "categorias/<int:pk>/",
        views.categoria_detalle,
        name="categoria_detalle"
    ),
    path(
        "votaciones/<int:pk>/",
        views.votacion_detalle,
        name="votacion_detalle"
    ),
    path(
        "votar/<int:pk>/confirmar/",
        views.confirmar_voto,
        name="confirmar_voto"
    ),
    path(
        "votar/<int:pk>/",
        views.registrar_voto,
        name="registrar_voto"
    ),
    path(
    "mis-votos/",
    views.mis_votos,
    name="mis_votos"
    ),
    # =========================================================
    # API
    # =========================================================

path(
    "api/categorias/",
    views.api_categorias,
    name="api_categorias"
),
]