from django.db import models


class Edicion(models.Model):
    anio = models.PositiveIntegerField(
        unique=True,
        verbose_name="Año"
    )
    nombre = models.CharField(
        max_length=150,
        verbose_name="Nombre"
    )
    descripcion = models.TextField(
        blank=True,
        verbose_name="Descripción"
    )
    fecha_inicio = models.DateField(
        verbose_name="Fecha de inicio"
    )
    fecha_fin = models.DateField(
        verbose_name="Fecha de finalización"
    )
    activa = models.BooleanField(
        default=True,
        verbose_name="Activa"
    )

    class Meta:
        verbose_name = "Edición"
        verbose_name_plural = "Ediciones"
        ordering = ["-anio"]

    def __str__(self):
        return f"{self.nombre} - {self.anio}"


class Categoria(models.Model):
    edicion = models.ForeignKey(
        Edicion,
        on_delete=models.CASCADE,
        related_name="categorias",
        verbose_name="Edición"
    )
    nombre = models.CharField(
        max_length=150,
        verbose_name="Nombre"
    )
    descripcion = models.TextField(
        blank=True,
        verbose_name="Descripción"
    )
    imagen = models.ImageField(
        upload_to="categorias/",
        blank=True,
        null=True,
        verbose_name="Imagen"
    )
    activa = models.BooleanField(
        default=True,
        verbose_name="Activa"
    )

    class Meta:
        verbose_name = "Categoría"
        verbose_name_plural = "Categorías"
        ordering = ["nombre"]
        constraints = [
            models.UniqueConstraint(
                fields=["edicion", "nombre"],
                name="categoria_unica_por_edicion"
            )
        ]

    def __str__(self):
        return f"{self.nombre} - {self.edicion.anio}"


class Votacion(models.Model):
    categoria = models.ForeignKey(
        Categoria,
        on_delete=models.CASCADE,
        related_name="votaciones",
        verbose_name="Categoría"
    )
    nombre = models.CharField(
        max_length=200,
        verbose_name="Nombre"
    )
    descripcion = models.TextField(
        blank=True,
        verbose_name="Descripción"
    )
    fecha_inicio = models.DateTimeField(
        verbose_name="Fecha y hora de inicio"
    )
    fecha_fin = models.DateTimeField(
        verbose_name="Fecha y hora de finalización"
    )
    activa = models.BooleanField(
        default=True,
        verbose_name="Activa"
    )

    class Meta:
        verbose_name = "Votación"
        verbose_name_plural = "Votaciones"
        ordering = ["-fecha_inicio"]

    def __str__(self):
        return self.nombre


class Opcion(models.Model):
    votacion = models.ForeignKey(
        Votacion,
        on_delete=models.CASCADE,
        related_name="opciones",
        verbose_name="Votación"
    )
    nombre = models.CharField(
        max_length=200,
        verbose_name="Nombre"
    )
    descripcion = models.TextField(
        blank=True,
        verbose_name="Descripción"
    )
    ciudad = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Ciudad"
    )
    imagen = models.ImageField(
        upload_to="opciones/",
        blank=True,
        null=True,
        verbose_name="Imagen"
    )
    activa = models.BooleanField(
        default=True,
        verbose_name="Activa"
    )

    class Meta:
        verbose_name = "Opción"
        verbose_name_plural = "Opciones"
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre

class Voto(models.Model):

    usuario = models.ForeignKey(
        "auth.User",
        on_delete=models.PROTECT,
        related_name="votos",
        verbose_name="Usuario que votó"
    )

    opcion = models.ForeignKey(
        Opcion,
        on_delete=models.PROTECT,
        related_name="votos",
        verbose_name="Opción seleccionada"
    )

    fecha_voto = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha del voto"
    )

    anulado = models.BooleanField(
        default=False,
        verbose_name="Voto anulado"
    )

    fecha_anulacion = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Fecha de anulación"
    )

    anulado_por = models.ForeignKey(
        "auth.User",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="votos_anulados",
        verbose_name="Anulado por"
    )

    motivo_anulacion = models.TextField(
        blank=True,
        verbose_name="Motivo de anulación"
    )

    class Meta:
        verbose_name = "Voto"
        verbose_name_plural = "Votos"
        ordering = ["-fecha_voto"]

    def __str__(self):
        estado = "ANULADO" if self.anulado else "VÁLIDO"

        return (
            f"{self.usuario.username} - "
            f"{self.opcion.nombre} - "
            f"{estado}"
        )


class AuditoriaVoto(models.Model):

    ACCIONES = [
        ("REGISTRADO", "Voto registrado"),
        ("ANULADO", "Voto anulado"),
    ]

    voto = models.ForeignKey(
        Voto,
        on_delete=models.PROTECT,
        related_name="auditoria",
        verbose_name="Voto"
    )

    accion = models.CharField(
        max_length=20,
        choices=ACCIONES,
        verbose_name="Acción"
    )

    realizado_por = models.ForeignKey(
        "auth.User",
        on_delete=models.PROTECT,
        related_name="acciones_auditoria_votos",
        verbose_name="Realizado por"
    )

    fecha = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha y hora"
    )

    detalle = models.TextField(
        blank=True,
        verbose_name="Detalle"
    )

    class Meta:
        verbose_name = "Auditoría de voto"
        verbose_name_plural = "Auditoría de votos"
        ordering = ["-fecha"]

    def __str__(self):
        return (
            f"{self.accion} - "
            f"{self.voto.usuario.username} - "
            f"{self.fecha}"
        )
    # =========================================================
# VISTAS ADMINISTRATIVAS DE VOTOS
# =========================================================


class VotoValido(Voto):

    class Meta:
        proxy = True
        verbose_name = "Voto válido"
        verbose_name_plural = "Votos válidos"


class VotoAnulado(Voto):

    class Meta:
        proxy = True
        verbose_name = "Voto anulado"
        verbose_name_plural = "Votos anulados"