from datetime import timedelta

from django.db import migrations
from django.utils import timezone


def crear_datos_iniciales(apps, schema_editor):
    User = apps.get_model('auth', 'User')
    Paciente = apps.get_model('pacientes', 'Paciente')
    Cita = apps.get_model('citas', 'Cita')
    SugerenciaCita = apps.get_model('citas', 'SugerenciaCita')

    admin_user, created = User.objects.get_or_create(
        username='admin',
        defaults={'email': 'admin@demo.com', 'is_staff': True, 'is_superuser': True},
    )
    admin_user.is_staff = True
    admin_user.is_superuser = True
    admin_user.first_name = admin_user.first_name or 'Administrador'
    admin_user.set_password('admin123')
    admin_user.save()

    pacientes_info = [
        {
            'username': 'paciente1',
            'password': 'paciente123',
            'dni': '12345678',
            'nombre_legal': 'Juan Pérez',
            'nombre_mostrado': 'Juan Pérez',
            'telefono': '999111222',
            'email': 'juan@example.com',
        },
        {
            'username': 'paciente2',
            'password': 'paciente123',
            'dni': '87654321',
            'nombre_legal': 'María García',
            'nombre_mostrado': 'María García',
            'telefono': '988777666',
            'email': 'maria@example.com',
        },
    ]

    pacientes_creados = []

    for info in pacientes_info:
        user, _ = User.objects.get_or_create(
            username=info['username'],
            defaults={'email': info['email'], 'first_name': info['nombre_mostrado']},
        )
        user.email = info['email']
        user.first_name = info['nombre_mostrado']
        user.is_staff = False
        user.is_superuser = False
        user.set_password(info['password'])
        user.save()

        paciente, _ = Paciente.objects.update_or_create(
            user=user,
            defaults={
                'dni': info['dni'],
                'nombre_legal': info['nombre_legal'],
                'nombre_mostrado': info['nombre_mostrado'],
                'telefono': info['telefono'],
                'email_contacto': info['email'],
            },
        )
        pacientes_creados.append(paciente)

    ahora = timezone.now()
    citas_datos = [
        (pacientes_creados[0], ahora + timedelta(days=1), ahora + timedelta(days=1, hours=1), 'Control general'),
        (pacientes_creados[0], ahora + timedelta(days=7), ahora + timedelta(days=7, hours=1), 'Revisión de laboratorio'),
        (pacientes_creados[1], ahora + timedelta(days=3), ahora + timedelta(days=3, hours=1), 'Consulta nutricional'),
    ]

    for paciente, inicio, fin, motivo in citas_datos:
        Cita.objects.get_or_create(
            paciente=paciente,
            fecha_hora_inicio=inicio,
            defaults={
                'fecha_hora_fin': fin,
                'motivo': motivo,
                'estado': 'PENDIENTE',
                'creada_por': admin_user,
                'actualizada_por': admin_user,
            },
        )

    if pacientes_creados:
        primera_cita = (
            Cita.objects.filter(paciente=pacientes_creados[0])
            .order_by('fecha_hora_inicio')
            .first()
        )
        SugerenciaCita.objects.get_or_create(
            paciente=pacientes_creados[0],
            mensaje='¿Podemos reprogramar mi cita más temprano?',
            defaults={'cita': primera_cita},
        )


def eliminar_datos_iniciales(apps, schema_editor):
    User = apps.get_model('auth', 'User')
    Paciente = apps.get_model('pacientes', 'Paciente')
    Cita = apps.get_model('citas', 'Cita')
    SugerenciaCita = apps.get_model('citas', 'SugerenciaCita')

    for username in ['paciente1', 'paciente2']:
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            continue
        SugerenciaCita.objects.filter(paciente__user=user).delete()
        Paciente.objects.filter(user=user).delete()
        user.delete()

    Cita.objects.filter(paciente__isnull=True).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('citas', '0001_initial'),
        ('pacientes', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(crear_datos_iniciales, eliminar_datos_iniciales),
    ]
