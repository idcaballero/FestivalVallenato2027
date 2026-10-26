from django.contrib import admin
from django.utils import timezone

from .models import (
    Edicion,
    Categoria,
    Votacion,
    Opcion,
    Voto,
    AuditoriaVoto,
    VotoValido,
    VotoAnulado,
)


@admin.register(Edicion)
class EdicionAdmin(admin.ModelAdmin):
    list_display = (
        "anio",
        "nombre",
        "fecha_inicio",
        "fecha_fin",
        "activa",
    )

    list_filter = (
        "activa",
        "anio",
    )

    search_fields = (
        "nombre",
    )


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = (
        "nombre",
        "edicion",
        "activa",
    )

    list_filter = (
        "edicion",
        "activa",
    )

    search_fields = (
        "nombre",
    )


@admin.register(Votacion)
class VotacionAdmin(admin.ModelAdmin):
    list_display = (
        "nombre",
        "categoria",
        "fecha_inicio",
        "fecha_fin",
        "activa",
    )

    list_filter = (
        "categoria",
        "activa",
    )

    search_fields = (
        "nombre",
    )


@admin.register(Opcion)
class OpcionAdmin(admin.ModelAdmin):
    list_display = (
        "nombre",
        "votacion",
        "ciudad",
        "activa",
    )

    list_filter = (
        "votacion",
        "activa",
    )

    search_fields = (
        "nombre",
        "ciudad",
    )


# =========================================================
# VOTOS VÁLIDOS
# =========================================================

@admin.register(VotoValido)
class VotoValidoAdmin(admin.ModelAdmin):

    list_display = (
        "numero_voto",
        "usuario",
        "opcion",
        "votacion_nombre",
        "fecha_voto",
        "estado",
    )

    list_filter = (
        "fecha_voto",
        "opcion__votacion",
    )

    search_fields = (
        "id",
        "usuario__username",
        "usuario__first_name",
        "usuario__last_name",
        "opcion__nombre",
        "opcion__votacion__nombre",
    )

    ordering = (
        "-fecha_voto",
    )

    readonly_fields = (
        "usuario",
        "opcion",
        "fecha_voto",
    )

    actions = [
        "anular_votos_seleccionados",
    ]


    def get_queryset(self, request):

        queryset = super().get_queryset(request)

        return queryset.filter(
            anulado=False
        )


    @admin.display(description="Voto")
    def numero_voto(self, obj):

        return f"#{obj.id}"


    @admin.display(description="Votación")
    def votacion_nombre(self, obj):

        return obj.opcion.votacion.nombre


    @admin.display(description="Estado")
    def estado(self, obj):

        return "VÁLIDO"


    @admin.action(
        description="Anular votos seleccionados"
    )
    def anular_votos_seleccionados(self, request, queryset):

        if not request.user.is_superuser:

            self.message_user(
                request,
                "Solo un superusuario puede anular votos.",
                level="ERROR",
            )

            return


        votos_anulados = 0


        for voto in queryset:

            if voto.anulado:
                continue


            voto.anulado = True
            voto.fecha_anulacion = timezone.now()
            voto.anulado_por = request.user

            voto.motivo_anulacion = (
                "Anulación realizada desde el panel administrativo."
            )

            voto.save()


            AuditoriaVoto.objects.create(
                voto=voto,
                accion="ANULADO",
                realizado_por=request.user,
                detalle=(
                    f"Voto #{voto.id} anulado. "
                    f"Usuario que emitió el voto: "
                    f"{voto.usuario.username}. "
                    f"Opción seleccionada: "
                    f"{voto.opcion.nombre}."
                ),
            )


            votos_anulados += 1


        self.message_user(
            request,
            f"{votos_anulados} voto(s) fueron anulados correctamente."
        )


    def has_add_permission(self, request):
        return False


    def has_delete_permission(self, request, obj=None):
        return False


# =========================================================
# VOTOS ANULADOS
# =========================================================

@admin.register(VotoAnulado)
class VotoAnuladoAdmin(admin.ModelAdmin):

    list_display = (
        "numero_voto",
        "usuario",
        "opcion",
        "votacion_nombre",
        "fecha_voto",
        "fecha_anulacion",
        "anulado_por",
    )

    list_filter = (
        "fecha_anulacion",
        "anulado_por",
        "opcion__votacion",
    )

    search_fields = (
        "id",
        "usuario__username",
        "usuario__first_name",
        "usuario__last_name",
        "opcion__nombre",
        "anulado_por__username",
    )

    ordering = (
        "-fecha_anulacion",
    )

    readonly_fields = (
        "usuario",
        "opcion",
        "fecha_voto",
        "anulado",
        "fecha_anulacion",
        "anulado_por",
        "motivo_anulacion",
    )


    def get_queryset(self, request):

        queryset = super().get_queryset(request)

        return queryset.filter(
            anulado=True
        )


    @admin.display(description="Voto")
    def numero_voto(self, obj):

        return f"#{obj.id}"


    @admin.display(description="Votación")
    def votacion_nombre(self, obj):

        return obj.opcion.votacion.nombre


    def has_add_permission(self, request):
        return False


    def has_delete_permission(self, request, obj=None):
        return False


    def has_change_permission(self, request, obj=None):

        # Se puede entrar al registro para consultarlo,
        # pero los campos son de solo lectura.
        return True

# =========================================================
# AUDITORÍA DE VOTOS
# =========================================================

@admin.register(AuditoriaVoto)
class AuditoriaVotoAdmin(admin.ModelAdmin):

    list_display = (
        "voto",
        "accion",
        "realizado_por",
        "fecha",
    )

    list_filter = (
        "accion",
        "fecha",
    )

    search_fields = (
        "voto__usuario__username",
        "voto__opcion__nombre",
        "realizado_por__username",
    )

    ordering = (
        "-fecha",
    )

    readonly_fields = (
        "voto",
        "accion",
        "realizado_por",
        "fecha",
        "detalle",
    )


    # La auditoría no se crea manualmente
    def has_add_permission(self, request):
        return False


    # La auditoría no se modifica
    def has_change_permission(self, request, obj=None):
        return False


    # La auditoría no se elimina
    def has_delete_permission(self, request, obj=None):
        return False