# Generated manually for initial schema
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Paciente',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dni', models.CharField(max_length=12, unique=True)),
                ('nombre_legal', models.CharField(max_length=150)),
                ('nombre_mostrado', models.CharField(max_length=150)),
                ('telefono', models.CharField(blank=True, max_length=20)),
                ('email_contacto', models.EmailField(blank=True, max_length=254)),
                (
                    'user',
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='paciente',
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
    ]
