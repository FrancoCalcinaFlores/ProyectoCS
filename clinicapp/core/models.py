from django.db import models
from django.conf import settings

class Notificacion(models.Model):
    CANAL = [('EMAIL', 'Email'), ('WEB', 'Web')]

    para = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notificaciones'
    )
    canal = models.CharField(max_length=10, choices=CANAL)
    asunto = models.CharField(max_length=150)
    cuerpo = models.TextField()
    ts = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.canal} → {self.para} | {self.asunto}"


from django.contrib.auth.models import User

class Bitacora(models.Model):
    entidad = models.CharField(max_length=50)
    entidad_id = models.CharField(max_length=50)
    accion = models.CharField(max_length=50)
    detalle = models.TextField(blank=True, null=True)
    fecha = models.DateTimeField(auto_now_add=True)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return f"{self.entidad} ({self.accion}) - {self.fecha}"


class Bitacora(models.Model):
    entidad = models.CharField(max_length=50)
    entidad_id = models.CharField(max_length=50)
    accion = models.CharField(max_length=50)
    detalle = models.TextField(blank=True, null=True)
    fecha = models.DateTimeField(auto_now_add=True)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return f"{self.entidad} ({self.accion}) - {self.fecha}"
