from django.db import models
from django.conf import settings
from pacientes.models import Paciente

ESTADO_CITA = [
    ('PENDIENTE', 'Pendiente'),
    ('CONFIRMADA', 'Confirmada'),
    ('REPROGRAMADA', 'Reprogramada'),
    ('CANCELADA', 'Cancelada'),
]

class Cita(models.Model):
    paciente = models.ForeignKey(
        Paciente, on_delete=models.CASCADE, related_name='citas'
    )
    fecha_hora_inicio = models.DateTimeField()
    fecha_hora_fin = models.DateTimeField()
    estado = models.CharField(max_length=12, choices=ESTADO_CITA, default='PENDIENTE')
    motivo = models.CharField(max_length=200, blank=True)

    creada_por = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, related_name='citas_creadas'
    )
    actualizada_por = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, related_name='citas_actualizadas'
    )

    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-fecha_hora_inicio']

    def __str__(self):
        return f"Cita {self.id} - {self.paciente} - {self.estado}"


class SugerenciaCita(models.Model):
    paciente = models.ForeignKey(
        Paciente, on_delete=models.CASCADE, related_name='sugerencias'
    )
    cita = models.ForeignKey(
        'Cita', on_delete=models.SET_NULL, null=True, blank=True, related_name='sugerencias'
    )
    mensaje = models.TextField()
    resuelta = models.BooleanField(default=False)
    creado_en = models.DateTimeField(auto_now_add=True)
    resuelta_en = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['resuelta', '-creado_en']
        verbose_name = 'sugerencia de cita'
        verbose_name_plural = 'sugerencias de citas'

    def __str__(self):
        return f"Sugerencia #{self.pk} de {self.paciente}"
