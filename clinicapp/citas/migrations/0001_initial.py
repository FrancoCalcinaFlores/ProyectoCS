# Generated manually for initial schema
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('pacientes', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Cita',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha_hora_inicio', models.DateTimeField()),
                ('fecha_hora_fin', models.DateTimeField()),
                (
                    'estado',
                    models.CharField(
                        choices=[
                            ('PENDIENTE', 'Pendiente'),
                            ('CONFIRMADA', 'Confirmada'),
                            ('REPROGRAMADA', 'Reprogramada'),
                            ('CANCELADA', 'Cancelada'),
                        ],
                        default='PENDIENTE',
                        max_length=12,
                    ),
                ),
                ('motivo', models.CharField(blank=True, max_length=200)),
                ('creado_en', models.DateTimeField(auto_now_add=True)),
                ('actualizado_en', models.DateTimeField(auto_now=True)),
                (
                    'actualizada_por',
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name='citas_actualizadas',
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    'creada_por',
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name='citas_creadas',
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    'paciente',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='citas',
                        to='pacientes.paciente',
                    ),
                ),
            ],
            options={'ordering': ['-fecha_hora_inicio']},
        ),
        migrations.CreateModel(
            name='SugerenciaCita',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('mensaje', models.TextField()),
                ('resuelta', models.BooleanField(default=False)),
                ('creado_en', models.DateTimeField(auto_now_add=True)),
                ('resuelta_en', models.DateTimeField(blank=True, null=True)),
                (
                    'cita',
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name='sugerencias',
                        to='citas.cita',
                    ),
                ),
                (
                    'paciente',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='sugerencias',
                        to='pacientes.paciente',
                    ),
                ),
            ],
            options={
                'verbose_name': 'sugerencia de cita',
                'verbose_name_plural': 'sugerencias de citas',
                'ordering': ['resuelta', '-creado_en'],
            },
        ),
    ]
