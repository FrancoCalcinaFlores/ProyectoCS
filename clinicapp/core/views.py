from django.shortcuts import render


def home(request):
    """Pantalla principal con accesos para pacientes y administradores."""

    return render(request, 'core/home.html')
