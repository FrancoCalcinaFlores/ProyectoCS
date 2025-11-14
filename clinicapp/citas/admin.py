from django.contrib import admin

from .models import Cita, SugerenciaCita


@admin.register(Cita)
class CitaAdmin(admin.ModelAdmin):
    list_display = ('id', 'paciente', 'fecha_hora_inicio', 'estado')
    list_filter = ('estado', 'fecha_hora_inicio')
    search_fields = ('paciente__nombre_mostrado', 'paciente__dni')


@admin.register(SugerenciaCita)
class SugerenciaCitaAdmin(admin.ModelAdmin):
    list_display = ('id', 'paciente', 'cita', 'resuelta', 'creado_en')
    list_filter = ('resuelta', 'creado_en')
    search_fields = ('paciente__nombre_mostrado', 'mensaje')
