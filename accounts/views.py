from django.shortcuts import render, redirect
from django.contrib.auth import login
from .forms import RegistroForm


def registro(request):
    if request.method == "POST":
        form = RegistroForm(request.POST)

        if form.is_valid():
            usuario = form.save()
            login(request, usuario)

            return redirect("votaciones:inicio")

    else:
        form = RegistroForm()

    context = {
        "form": form
    }

    return render(
        request,
        "accounts/registro.html",
        context
    )