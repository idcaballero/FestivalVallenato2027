from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.db import transaction, IntegrityError
from django.utils import timezone
from django.http import JsonResponse
from django.views.decorators.http import require_GET

from .models import (
    Edicion,
    Categoria,
    Votacion,
    Opcion,
    Voto,
    AuditoriaVoto,
)


# =========================================================
# PÁGINA PRINCIPAL
# =========================================================

def inicio(request):

    edicion = (
        Edicion.objects
        .filter(activa=True)
        .first()
    )

    categorias = (
        Categoria.objects
        .filter(activa=True)
        .select_related("edicion")
        .order_by("nombre")
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

    # Usuario no autenticado
    if not usuario.is_authenticated:
        return False

    # Administradores y superusuarios no pueden votar
    if usuario.is_superuser or usuario.is_staff:
        return False

    # Los miembros del grupo Jurado tampoco pueden votar
    if usuario.groups.filter(name="Jurado").exists():
        return False

    # Usuario regular
    return True


# =========================================================
# LISTADO DE CATEGORÍAS
# =========================================================

def categorias(request):

    categorias = (
        Categoria.objects
        .filter(activa=True)
        .select_related("edicion")
        .order_by("nombre")
    )

    return render(
        request,
        "votaciones/categorias.html",
        {
            "categorias": categorias,
        }
    )


# =========================================================
# DETALLE DE CATEGORÍA
# =========================================================

def categoria_detalle(request, pk):

    categoria = get_object_or_404(
        Categoria.objects.select_related("edicion"),
        pk=pk,
        activa=True
    )

    votaciones = (
        categoria.votaciones
        .filter(activa=True)
        .order_by("fecha_inicio")
    )

    return render(
        request,
        "votaciones/categoria_detalle.html",
        {
            "categoria": categoria,
            "votaciones": votaciones,
        }
    )


# =========================================================
# DETALLE DE VOTACIÓN
# =========================================================

def votacion_detalle(request, pk):

    votacion = get_object_or_404(
        Votacion.objects.select_related(
            "categoria__edicion"
        ),
        pk=pk,
        activa=True
    )

    opciones = (
        votacion.opciones
        .filter(activa=True)
        .order_by("nombre")
    )

    categoria = votacion.categoria
    edicion = categoria.edicion

    voto_usuario = None

    # -----------------------------------------------------
    # IMPORTANTE:
    # El voto se busca solamente dentro de ESTA categoría
    # y ESTA edición.
    # -----------------------------------------------------

    if request.user.is_authenticated:

        voto_usuario = (
            Voto.objects
            .filter(
                usuario=request.user,
                edicion=edicion,
                categoria=categoria,
                anulado=False
            )
            .select_related(
                "opcion",
                "categoria",
                "edicion"
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


# =========================================================
# CONFIRMACIÓN DEL VOTO
# =========================================================

@login_required
def confirmar_voto(request, pk):

    # -----------------------------------------------------
    # 1. Verificar permisos
    # -----------------------------------------------------

    if not usuario_puede_votar(request.user):

        messages.warning(
            request,
            "Tu tipo de usuario no tiene permiso para participar "
            "en las votaciones."
        )

        return redirect(
            "votaciones:inicio"
        )

    # -----------------------------------------------------
    # 2. Obtener opción y relaciones
    # -----------------------------------------------------

    opcion = get_object_or_404(
        Opcion.objects.select_related(
            "votacion__categoria__edicion"
        ),
        pk=pk,
        activa=True
    )

    votacion = opcion.votacion
    categoria = votacion.categoria
    edicion = categoria.edicion

    ahora = timezone.now()

    # -----------------------------------------------------
    # 3. Verificar edición activa
    # -----------------------------------------------------

    if not edicion.activa:

        messages.warning(
            request,
            "La edición del Festival no se encuentra habilitada "
            "para votación."
        )

        return redirect(
            "votaciones:votacion_detalle",
            pk=votacion.pk
        )

    # -----------------------------------------------------
    # 4. Verificar categoría activa
    # -----------------------------------------------------

    if not categoria.activa:

        messages.warning(
            request,
            "Esta categoría no se encuentra habilitada para votar."
        )

        return redirect(
            "votaciones:votacion_detalle",
            pk=votacion.pk
        )

    # -----------------------------------------------------
    # 5. Verificar votación activa
    # -----------------------------------------------------

    if not votacion.activa:

        messages.warning(
            request,
            "Esta votación se encuentra cerrada."
        )

        return redirect(
            "votaciones:votacion_detalle",
            pk=votacion.pk
        )

    # -----------------------------------------------------
    # 6. Verificar fecha de apertura
    # -----------------------------------------------------

    if (
        votacion.fecha_inicio
        and ahora < votacion.fecha_inicio
    ):

        messages.warning(
            request,
            "La votación todavía no ha comenzado."
        )

        return redirect(
            "votaciones:votacion_detalle",
            pk=votacion.pk
        )

    # -----------------------------------------------------
    # 7. Verificar fecha de cierre
    # -----------------------------------------------------

    if (
        votacion.fecha_fin
        and ahora > votacion.fecha_fin
    ):

        messages.warning(
            request,
            "El período de votación ya finalizó."
        )

        return redirect(
            "votaciones:votacion_detalle",
            pk=votacion.pk
        )

    # -----------------------------------------------------
    # 8. Verificar voto previo SOLAMENTE en esta categoría
    # -----------------------------------------------------

    voto_existente = (
        Voto.objects
        .filter(
            usuario=request.user,
            edicion=edicion,
            categoria=categoria,
            anulado=False
        )
        .exists()
    )

    if voto_existente:

        messages.warning(
            request,
            "Ya registraste un voto en esta categoría."
        )

        return redirect(
            "votaciones:votacion_detalle",
            pk=votacion.pk
        )

    # -----------------------------------------------------
    # 9. Mostrar confirmación
    # -----------------------------------------------------

    return render(
        request,
        "votaciones/confirmar_voto.html",
        {
            "opcion": opcion,
            "votacion": votacion,
            "categoria": categoria,
            "edicion": edicion,
        }
    )


# =========================================================
# REGISTRAR VOTO
# =========================================================

@login_required
@require_POST
def registrar_voto(request, pk):

    # -----------------------------------------------------
    # 1. Verificar permisos
    # -----------------------------------------------------

    if not usuario_puede_votar(request.user):

        messages.warning(
            request,
            "Tu tipo de usuario no tiene permiso para participar "
            "en las votaciones."
        )

        return redirect(
            "votaciones:inicio"
        )

    # -----------------------------------------------------
    # 2. Obtener opción y relaciones
    # -----------------------------------------------------

    opcion = get_object_or_404(
        Opcion.objects.select_related(
            "votacion__categoria__edicion"
        ),
        pk=pk
    )

    votacion = opcion.votacion
    categoria = votacion.categoria
    edicion = categoria.edicion

    ahora = timezone.now()

    # -----------------------------------------------------
    # 3. Validar edición activa
    # -----------------------------------------------------

    if not edicion.activa:

        messages.warning(
            request,
            "La edición del Festival no se encuentra habilitada "
            "para votación."
        )

        return redirect(
            "votaciones:votacion_detalle",
            pk=votacion.pk
        )

    # -----------------------------------------------------
    # 4. Validar categoría activa
    # -----------------------------------------------------

    if not categoria.activa:

        messages.warning(
            request,
            "Esta categoría no se encuentra habilitada para votar."
        )

        return redirect(
            "votaciones:votacion_detalle",
            pk=votacion.pk
        )

    # -----------------------------------------------------
    # 5. Validar votación activa
    # -----------------------------------------------------

    if not votacion.activa:

        messages.warning(
            request,
            "Esta votación se encuentra cerrada."
        )

        return redirect(
            "votaciones:votacion_detalle",
            pk=votacion.pk
        )

    # -----------------------------------------------------
    # 6. Validar opción activa
    # -----------------------------------------------------

    if not opcion.activa:

        messages.warning(
            request,
            "El participante seleccionado no se encuentra habilitado."
        )

        return redirect(
            "votaciones:votacion_detalle",
            pk=votacion.pk
        )

    # -----------------------------------------------------
    # 7. Validar fecha de inicio
    # -----------------------------------------------------

    if (
        votacion.fecha_inicio
        and ahora < votacion.fecha_inicio
    ):

        messages.warning(
            request,
            "La votación todavía no ha comenzado."
        )

        return redirect(
            "votaciones:votacion_detalle",
            pk=votacion.pk
        )

    # -----------------------------------------------------
    # 8. Validar fecha de cierre
    # -----------------------------------------------------

    if (
        votacion.fecha_fin
        and ahora > votacion.fecha_fin
    ):

        messages.warning(
            request,
            "El período de votación ya finalizó."
        )

        return redirect(
            "votaciones:votacion_detalle",
            pk=votacion.pk
        )

    # -----------------------------------------------------
    # 9. Validar categoría enviada por formulario
    # -----------------------------------------------------

    categoria_enviada = request.POST.get(
        "categoria_id"
    )

    if (
        categoria_enviada
        and categoria_enviada != str(categoria.id)
    ):

        messages.error(
            request,
            "La opción seleccionada no corresponde "
            "a la categoría indicada."
        )

        return redirect(
            "votaciones:votacion_detalle",
            pk=votacion.pk
        )

    # -----------------------------------------------------
    # 10. Validar edición enviada por formulario
    # -----------------------------------------------------

    edicion_enviada = request.POST.get(
        "edicion_id"
    )

    if (
        edicion_enviada
        and edicion_enviada != str(edicion.id)
    ):

        messages.error(
            request,
            "La opción seleccionada no corresponde "
            "a la edición indicada."
        )

        return redirect(
            "votaciones:votacion_detalle",
            pk=votacion.pk
        )

    # -----------------------------------------------------
    # 11. Verificar voto existente
    #
    # IMPORTANTE:
    # La regla es usuario + edición + categoría.
    #
    # NO estamos buscando solamente por usuario.
    # -----------------------------------------------------

    voto_existente = (
        Voto.objects
        .filter(
            usuario=request.user,
            edicion=edicion,
            categoria=categoria,
            anulado=False
        )
        .exists()
    )

    if voto_existente:

        messages.warning(
            request,
            "Ya registraste un voto en esta categoría."
        )

        return redirect(
            "votaciones:votacion_detalle",
            pk=votacion.pk
        )

    # -----------------------------------------------------
    # 12. Crear voto
    # -----------------------------------------------------

    try:

        with transaction.atomic():

            voto = Voto.objects.create(
                usuario=request.user,
                edicion=edicion,
                categoria=categoria,
                opcion=opcion
            )

            AuditoriaVoto.objects.create(
                voto=voto,
                accion="REGISTRADO",
                realizado_por=request.user,
                detalle=(
                    f"Voto registrado en la categoría "
                    f"{categoria.nombre} para la opción "
                    f"{opcion.nombre}."
                )
            )

    # -----------------------------------------------------
    # 13. MySQL como segunda barrera de seguridad
    # -----------------------------------------------------

    except IntegrityError:

        messages.warning(
            request,
            "No fue posible registrar el voto porque ya existe "
            "un voto válido para esta categoría."
        )

        return redirect(
            "votaciones:votacion_detalle",
            pk=votacion.pk
        )

    # -----------------------------------------------------
    # 14. Confirmación
    # -----------------------------------------------------

    messages.success(
        request,
        f"Tu voto por {opcion.nombre} fue registrado correctamente."
    )

    return redirect(
        "votaciones:votacion_detalle",
        pk=votacion.pk
    )
from django.contrib.auth.decorators import login_required


@login_required
def mis_votos(request):
    votos = (
        Voto.objects
        .filter(
            usuario=request.user,
            anulado=False
        )
        .select_related(
            "edicion",
            "categoria",
            "opcion"
        )
        .order_by("categoria__nombre")
    )

    return render(
        request,
        "votaciones/mis_votos.html",
        {
            "votos": votos
        }
    )
# =========================================================
# API GET - CATEGORÍAS Y OPCIONES
# =========================================================

@require_GET
def api_categorias(request):

    categorias = (
        Categoria.objects
        .filter(activa=True)
        .select_related("edicion")
        .order_by("nombre")
    )

    datos = []

    for categoria in categorias:

        votaciones = (
            Votacion.objects
            .filter(
                categoria=categoria,
                activa=True
            )
            .order_by("nombre")
        )

        opciones = (
            Opcion.objects
            .filter(
                votacion__categoria=categoria,
                votacion__activa=True,
                activa=True
            )
            .select_related("votacion")
            .order_by("nombre")
        )

        categoria_data = {
            "id": categoria.id,
            "nombre": categoria.nombre,
            "edicion": categoria.edicion.anio,
            "activa": categoria.activa,

            "votaciones": [
                {
                    "id": votacion.id,
                    "nombre": votacion.nombre
                }
                for votacion in votaciones
            ],

            "opciones": [
                {
                    "id": opcion.id,
                    "nombre": opcion.nombre,
                    "votacion_id": opcion.votacion.id,
                    "votacion": opcion.votacion.nombre
                }
                for opcion in opciones
            ]
        }

        datos.append(categoria_data)

    return JsonResponse(
        {
            "categorias": datos
        },
        json_dumps_params={
            "ensure_ascii": False,
            "indent": 2
        }
    )