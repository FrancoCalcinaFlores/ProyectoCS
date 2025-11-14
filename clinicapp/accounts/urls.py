from django.urls import path

from . import views

app_name = 'accounts'

urlpatterns = [
    path('login/paciente/', views.PacienteLoginView.as_view(), name='login_paciente'),
    path('login/admin/', views.AdminLoginView.as_view(), name='login_admin'),
    path('logout/', views.SimpleLogoutView.as_view(), name='logout'),
    path('paciente/dashboard/', views.paciente_dashboard, name='dashboard_paciente'),
    path('admin/dashboard/', views.admin_dashboard, name='dashboard_admin'),
    path('admin/pacientes/<int:pk>/editar/', views.editar_paciente, name='editar_paciente'),
]
