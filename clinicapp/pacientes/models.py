from django.db import models
from django.conf import settings  # usar AUTH_USER_MODEL

class Paciente(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='paciente'
    )
    dni = models.CharField(max_length=12, unique=True)
    nombre_legal = models.CharField(max_length=150)
    nombre_mostrado = models.CharField(max_length=150)
    telefono = models.CharField(max_length=20, blank=True)
    email_contacto = models.EmailField(blank=True)

    def __str__(self):
        return f"{self.nombre_mostrado} ({self.dni})"
