from django.contrib import admin

from .models import Paciente


@admin.register(Paciente)
class PacienteAdmin(admin.ModelAdmin):
    list_display = ('nombre_mostrado', 'dni', 'telefono', 'email_contacto')
    search_fields = ('nombre_mostrado', 'dni')
