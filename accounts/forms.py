from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User


class RegistroForm(UserCreationForm):

    username = forms.CharField(
        label="Nombre de usuario",
        help_text="Máximo 150 caracteres. Puede contener letras, números y los caracteres @/./+/-/_"
    )

    first_name = forms.CharField(
        label="Nombre",
        required=True
    )

    last_name = forms.CharField(
        label="Apellido",
        required=True
    )

    email = forms.EmailField(
        label="Correo electrónico",
        required=True
    )

    class Meta:
        model = User

        fields = [
            "username",
            "first_name",
            "last_name",
            "email",
            "password1",
            "password2",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["password1"].label = "Contraseña"
        self.fields["password2"].label = "Confirmar contraseña"

        self.fields["password1"].help_text = (
            "La contraseña debe tener al menos 8 caracteres, "
            "no puede ser demasiado similar a tus datos personales, "
            "no puede ser una contraseña común y no puede contener únicamente números."
        )

        self.fields["password2"].help_text = (
            "Ingresa nuevamente la misma contraseña para verificarla."
        )


class InicioSesionForm(AuthenticationForm):

    username = forms.CharField(
        label="Nombre de usuario"
    )

    password = forms.CharField(
        label="Contraseña",
        widget=forms.PasswordInput
    )