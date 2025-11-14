from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User, Group
from django.utils import timezone
from datetime import timedelta

from pacientes.models import Paciente
from citas.models import Cita
from consultas.models import Consulta
from core.models import Bitacora
from citas.services import crear_cita
from consultas.services import crear_consulta, resolver_consulta


class BaseTestDataMixin:
    """Crea datos base: grupos, usuarios, paciente y cliente de prueba."""

    def setUp(self):
        # Grupos
        self.grp_paciente, _ = Group.objects.get_or_create(name='PACIENTE')
        self.grp_admin, _ = Group.objects.get_or_create(name='ADMIN')

        # Admin
        self.admin = User.objects.create_user(
            username='admin_test', password='admin123'
        )
        self.admin.groups.add(self.grp_admin)

        # Paciente
        self.user_paciente = User.objects.create_user(
            username='paciente_test', password='1234'
        )
        self.user_paciente.groups.add(self.grp_paciente)
        self.paciente = Paciente.objects.create(
            user=self.user_paciente,
            dni='12345678',
            nombre_legal='PACIENTE LEGAL',
            nombre_mostrado='Paciente Test',
            telefono='999999999',
            email_contacto='paciente@test.com'
        )

        self.client = Client()


class ModeloYServicioTests(BaseTestDataMixin, TestCase):
    """
    Pruebas unitarias de modelos y servicios:
    Paciente, Cita, Consulta y Bitacora.
    """

    # 1) Verificar que el modelo Paciente se asocia correctamente a User
    def test_paciente_asociado_a_usuario(self):
        self.assertEqual(self.paciente.user.username, 'paciente_test')
        self.assertTrue(self.user_paciente.paciente)   # related_name='paciente'

    # 2) Probar el __str__ de Cita
    def test_str_de_cita(self):
        inicio = timezone.now()
        fin = inicio + timedelta(hours=1)
        cita = Cita.objects.create(
            paciente=self.paciente,
            fecha_hora_inicio=inicio,
            fecha_hora_fin=fin,
            estado='PENDIENTE',
            motivo='Chequeo',
            creada_por=self.admin,
            actualizada_por=self.admin
        )
        self.assertIn('Cita', str(cita))
        self.assertIn('PENDIENTE', str(cita))

    # 3) crear_cita no permite solapamiento de citas para el mismo paciente
    def test_crear_cita_no_permite_solapamiento(self):
        inicio = timezone.now()
        fin = inicio + timedelta(hours=1)
        crear_cita(self.paciente, inicio, fin, 'Chequeo', self.admin)

        # Intento solapado
        with self.assertRaises(ValueError):
            crear_cita(
                self.paciente,
                inicio + timedelta(minutes=30),
                fin + timedelta(minutes=30),
                'Otro motivo',
                self.admin
            )

    # 4) crear_cita registra una entrada en Bitacora
    def test_crear_cita_registra_bitacora(self):
        inicio = timezone.now()
        fin = inicio + timedelta(hours=1)
        cita = crear_cita(self.paciente, inicio, fin, 'Chequeo', self.admin)

        existe = Bitacora.objects.filter(
            entidad='Cita', entidad_id=str(cita.id), accion='CREAR'
        ).exists()
        self.assertTrue(existe)

    # 5) resolver_consulta cambia el estado a RESUELTA
    def test_resolver_consulta_cambia_estado(self):
        consulta = crear_consulta(
            paciente=self.paciente,
            categoria='CANCELACION',
            descripcion='Quiero cancelar',
            cita=None
        )
        resolver_consulta(consulta, self.admin, 'Aprobado', aprobar=True)
        consulta.refresh_from_db()
        self.assertEqual(consulta.estado, 'RESUELTA')
        self.assertIn('Aprobado', consulta.respuesta_admin)

    # 6) resolver_consulta registra la acción en Bitacora
    def test_resolver_consulta_registra_bitacora(self):
        consulta = crear_consulta(
            paciente=self.paciente,
            categoria='REPROGRAMACION',
            descripcion='Otra fecha',
            cita=None
        )
        resolver_consulta(consulta, self.admin, 'Reprogramado', aprobar=True)
        existe = Bitacora.objects.filter(
            entidad='Consulta', entidad_id=str(consulta.id), accion='RESOLVER'
        ).exists()
        self.assertTrue(existe)


class VistasYLoginTests(BaseTestDataMixin, TestCase):
    """
    Pruebas unitarias de vistas:
    login, dashboard y calendario de paciente.
    """

    # 7) Login de paciente redirige al calendario del paciente
    def test_login_paciente_redirige_a_calendario(self):
        resp = self.client.post(
            reverse('login'),
            {'username': 'paciente_test', 'password': '1234'}
        )
        # Login ok -> redirige al dashboard
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp.url, reverse('dashboard'))

        # Dashboard debe redirigir al calendario del paciente
        resp2 = self.client.get(resp.url)
        self.assertEqual(resp2.status_code, 302)
        self.assertEqual(resp2.url, reverse('paciente_calendario'))

    # 8) Login de admin redirige al módulo de administrador
    def test_login_admin_redirige_a_admin(self):
        resp = self.client.post(
            reverse('login'),
            {'username': 'admin_test', 'password': 'admin123'}
        )
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp.url, reverse('dashboard'))

        resp2 = self.client.get(resp.url)
        self.assertEqual(resp2.status_code, 302)
        self.assertEqual(resp2.url, reverse('admin_consultas_list'))

    # 9) El calendario del paciente solo muestra sus propias citas
    def test_calendario_muestra_solo_citas_del_paciente(self):
        inicio = timezone.now()
        fin = inicio + timedelta(hours=1)

        # Cita del paciente de prueba
        crear_cita(self.paciente, inicio, fin, 'Chequeo', self.admin)

        # Otro paciente con otra cita
        otro_user = User.objects.create_user(
            username='otro', password='abcd'
        )
        otro_user.groups.add(self.grp_paciente)
        otro_paciente = Paciente.objects.create(
            user=otro_user,
            dni='87654321',
            nombre_legal='OTRO PACIENTE',
            nombre_mostrado='Otro',
            telefono='111111111',
            email_contacto='otro@test.com'
        )
        crear_cita(
            otro_paciente,
            inicio + timedelta(days=1),
            fin + timedelta(days=1),
            'Consulta',
            self.admin
        )

        # Login como paciente_test
        self.client.login(username='paciente_test', password='1234')
        resp = self.client.get(reverse('paciente_calendario'))

        self.assertEqual(resp.status_code, 200)
        citas = resp.context['citas']
        # Solo debe haber citas del paciente_test
        self.assertTrue(all(c.paciente == self.paciente for c in citas))
