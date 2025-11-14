from django.db import models
from pacientes.models import Paciente
from citas.models import Cita

CATEGORIAS = [
    ('CORRECCION_NOMBRE', 'Corrección de nombre'),
    ('REPROGRAMACION', 'Reprogramación de fecha'),
    ('CANCELACION', 'Cancelación de cita'),
]

ESTADO_CONSULTA = [
    ('ABIERTA', 'Abierta'),
    ('EN_PROCESO', 'En proceso'),
    ('RESUELTA', 'Resuelta'),
    ('RECHAZADA', 'Rechazada'),
]

class Consulta(models.Model):
    paciente = models.ForeignKey(
        Paciente, on_delete=models.CASCADE, related_name='consultas'
    )
    categoria = models.CharField(max_length=30, choices=CATEGORIAS)
    cita_opcional = models.ForeignKey(
        Cita, on_delete=models.SET_NULL, null=True, blank=True, related_name='consultas'
    )
    descripcion = models.TextField(blank=True)
    estado = models.CharField(max_length=15, choices=ESTADO_CONSULTA, default='ABIERTA')
    respuesta_admin = models.TextField(blank=True)
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.get_categoria_display()} - {self.paciente}"
