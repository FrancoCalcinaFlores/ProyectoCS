from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils import timezone

from citas.models import Cita, SugerenciaCita
from pacientes.models import Paciente

from .forms import (
    CitaForm,
    PacienteCreationForm,
    PacienteUpdateForm,
    SugerenciaForm,
    UsuarioUpdateForm,
)


class PacienteLoginView(LoginView):
    template_name = 'accounts/login.html'
    redirect_authenticated_user = True

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Ingreso de paciente'
        context['accion'] = 'paciente'
        return context

    def form_valid(self, form):
        user = form.get_user()
        if not hasattr(user, 'paciente'):
            form.add_error(None, 'Este usuario no está registrado como paciente.')
            return self.form_invalid(form)
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('accounts:dashboard_paciente')


class AdminLoginView(LoginView):
    template_name = 'accounts/login.html'
    redirect_authenticated_user = True

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Ingreso de administrador'
        context['accion'] = 'admin'
        return context

    def form_valid(self, form):
        user = form.get_user()
        if not user.is_staff:
            form.add_error(None, 'Este usuario no tiene permisos de administrador.')
            return self.form_invalid(form)
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('accounts:dashboard_admin')


class SimpleLogoutView(LogoutView):
    next_page = reverse_lazy('core:home')


@login_required
def paciente_dashboard(request):
    if not hasattr(request.user, 'paciente'):
        messages.error(request, 'Tu usuario no está vinculado con un paciente.')
        logout(request)
        return redirect('accounts:login_paciente')

    paciente = request.user.paciente
    citas = paciente.citas.order_by('fecha_hora_inicio')

    cita_form = CitaForm()
    sugerencia_form = SugerenciaForm(paciente=paciente)

    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'crear_cita':
            cita_form = CitaForm(request.POST)
            if cita_form.is_valid():
                nueva_cita = cita_form.save(commit=False)
                nueva_cita.paciente = paciente
                nueva_cita.creada_por = request.user
                nueva_cita.actualizada_por = request.user
                nueva_cita.estado = 'PENDIENTE'
                nueva_cita.save()
                messages.success(request, 'Cita registrada correctamente.')
                return redirect('accounts:dashboard_paciente')
        elif action == 'enviar_sugerencia':
            sugerencia_form = SugerenciaForm(request.POST, paciente=paciente)
            if sugerencia_form.is_valid():
                sugerencia = sugerencia_form.save(commit=False)
                sugerencia.paciente = paciente
                sugerencia.save()
                messages.success(request, 'Sugerencia enviada al administrador.')
                return redirect('accounts:dashboard_paciente')

    sugerencias = paciente.sugerencias.order_by('-creado_en')

    return render(
        request,
        'accounts/paciente_dashboard.html',
        {
            'paciente': paciente,
            'citas': citas,
            'cita_form': cita_form,
            'sugerencia_form': sugerencia_form,
            'sugerencias': sugerencias,
        },
    )


@login_required
def admin_dashboard(request):
    if not request.user.is_staff:
        messages.error(request, 'Debes ingresar como administrador para ver esta página.')
        logout(request)
        return redirect('accounts:login_admin')

    pacientes = Paciente.objects.select_related('user').order_by('nombre_mostrado')
    citas = Cita.objects.select_related('paciente', 'paciente__user').order_by('fecha_hora_inicio')
    sugerencias = SugerenciaCita.objects.select_related('paciente', 'cita').order_by('resuelta', '-creado_en')

    crear_form = PacienteCreationForm()

    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'crear_paciente':
            crear_form = PacienteCreationForm(request.POST)
            if crear_form.is_valid():
                crear_form.save()
                messages.success(request, 'Paciente creado correctamente.')
                return redirect('accounts:dashboard_admin')
        elif action == 'resolver_sugerencia':
            sugerencia_id = request.POST.get('sugerencia_id')
            sugerencia = get_object_or_404(SugerenciaCita, pk=sugerencia_id)
            sugerencia.resuelta = True
            sugerencia.resuelta_en = timezone.now()
            sugerencia.save(update_fields=['resuelta', 'resuelta_en'])
            messages.success(request, 'Sugerencia marcada como resuelta.')
            return redirect('accounts:dashboard_admin')

    return render(
        request,
        'accounts/admin_dashboard.html',
        {
            'pacientes': pacientes,
            'citas': citas,
            'sugerencias': sugerencias,
            'crear_form': crear_form,
        },
    )


@login_required
def editar_paciente(request, pk):
    if not request.user.is_staff:
        messages.error(request, 'Debes ingresar como administrador para ver esta página.')
        logout(request)
        return redirect('accounts:login_admin')

    paciente = get_object_or_404(Paciente, pk=pk)

    if request.method == 'POST':
        paciente_form = PacienteUpdateForm(request.POST, instance=paciente)
        usuario_form = UsuarioUpdateForm(request.POST, instance=paciente.user)
        if paciente_form.is_valid() and usuario_form.is_valid():
            paciente_form.save()
            usuario_form.save()
            messages.success(request, 'Datos del paciente actualizados correctamente.')
            return redirect('accounts:dashboard_admin')
    else:
        paciente_form = PacienteUpdateForm(instance=paciente)
        usuario_form = UsuarioUpdateForm(instance=paciente.user)

    return render(
        request,
        'accounts/admin_editar_paciente.html',
        {
            'paciente': paciente,
            'paciente_form': paciente_form,
            'usuario_form': usuario_form,
        },
    )
