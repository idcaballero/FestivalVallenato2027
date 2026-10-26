from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.db import transaction

from .models import (
    Edicion,
    Categoria,
    Votacion,
    Opcion,
    Voto,
    AuditoriaVoto,
)


def inicio(request):
    edicion = Edicion.objects.filter(
        activa=True
    ).first()

    categorias = (
        Categoria.objects
        .filter(activa=True)
        .select_related("edicion")
    )

    return render(
        request,
        "votaciones/inicio.html",
        {
            "edicion": edicion,
            "categorias": categorias,
        }
    )
# =========================================================
# CONTROL DE ROLES Y PERMISOS
# =========================================================

def usuario_puede_votar(usuario):

    if not usuario.is_authenticated:
        return False

    # Administradores y superusuarios no pueden votar
    if usuario.is_superuser or usuario.is_staff:
        return False

    # Los miembros del grupo Jurado tampoco pueden votar
    if usuario.groups.filter(name="Jurado").exists():
        return False

    return True

def categorias(request):
    categorias = (
        Categoria.objects
        .filter(activa=True)
        .select_related("edicion")
    )

    return render(
        request,
        "votaciones/categorias.html",
        {
            "categorias": categorias,
        }
    )


def categoria_detalle(request, pk):
    categoria = get_object_or_404(
        Categoria,
        pk=pk,
        activa=True
    )

    votaciones = categoria.votaciones.filter(
        activa=True
    )

    return render(
        request,
        "votaciones/categoria_detalle.html",
        {
            "categoria": categoria,
            "votaciones": votaciones,
        }
    )


def votacion_detalle(request, pk):
    votacion = get_object_or_404(
        Votacion,
        pk=pk,
        activa=True
    )

    opciones = votacion.opciones.filter(
        activa=True
    )

    voto_usuario = None

    if request.user.is_authenticated:

        voto_usuario = (
            Voto.objects
            .filter(
                 usuario=request.user,
                opcion__votacion__categoria=votacion.categoria,
                anulado=False,
            )
            .select_related(
                 "opcion",
                 "opcion__votacion",
                "opcion__votacion__categoria",
            )
            .first()
    )
    puede_votar = usuario_puede_votar(request.user)

    return render(
        request,
        "votaciones/votacion_detalle.html",
        {
            "votacion": votacion,
            "opciones": opciones,
            "voto_usuario": voto_usuario,
            "puede_votar": puede_votar,
        }
    )


@login_required
@require_POST
def registrar_voto(request, pk):

    if not usuario_puede_votar(request.user):

        messages.warning(
            request,
            "Tu tipo de usuario no tiene permiso para participar en las votaciones."
        )

        return redirect(
            "votaciones:inicio"
        )

    opcion = get_object_or_404(
        Opcion,
        pk=pk,
        activa=True
    )

    votacion = opcion.votacion


    # Verificar que el usuario no tenga
    # otro voto ACTIVO en esta votación.
    voto_existente = Voto.objects.filter(
         usuario=request.user,
         opcion__votacion__categoria=votacion.categoria,
         anulado=False,
    ).exists()


    if voto_existente:

        messages.warning(
    request,
    "Ya registraste un voto en esta categoría."
        )

        return redirect(
            "votaciones:votacion_detalle",
            pk=votacion.pk
        )


    # Registrar voto + auditoría como una sola operación.
    with transaction.atomic():

        voto = Voto.objects.create(
            usuario=request.user,
            opcion=opcion
        )

        AuditoriaVoto.objects.create(
            voto=voto,
            accion="REGISTRADO",
            realizado_por=request.user,
            detalle=(
                f"Voto registrado por el usuario "
                f"{request.user.username}. "
                f"Opción seleccionada: {opcion.nombre}. "
                f"Votación: {votacion.nombre}."
            ),
        )


    messages.success(
        request,
        f"Tu voto por {opcion.nombre} fue registrado correctamente."
    )


    return redirect(
        "votaciones:votacion_detalle",
        pk=votacion.pk
    )