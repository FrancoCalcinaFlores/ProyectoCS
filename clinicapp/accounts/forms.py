from django import forms
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

from citas.models import Cita, SugerenciaCita
from pacientes.models import Paciente


class CitaForm(forms.ModelForm):
    class Meta:
        model = Cita
        fields = ['fecha_hora_inicio', 'fecha_hora_fin', 'motivo']
        widgets = {
            'fecha_hora_inicio': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'fecha_hora_fin': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'motivo': forms.TextInput(attrs={'placeholder': 'Motivo opcional'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        inicio = cleaned_data.get('fecha_hora_inicio')
        fin = cleaned_data.get('fecha_hora_fin')
        if inicio and fin and fin <= inicio:
            raise ValidationError('La hora de fin debe ser posterior a la de inicio.')
        return cleaned_data


class SugerenciaForm(forms.ModelForm):
    class Meta:
        model = SugerenciaCita
        fields = ['cita', 'mensaje']
        widgets = {
            'mensaje': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Escribe aquí tu sugerencia'}),
        }

    def __init__(self, *args, **kwargs):
        paciente = kwargs.pop('paciente', None)
        super().__init__(*args, **kwargs)
        if paciente is not None:
            self.fields['cita'].queryset = paciente.citas.order_by('-fecha_hora_inicio')
        else:
            self.fields['cita'].queryset = Cita.objects.none()
        self.fields['cita'].required = False


class PacienteCreationForm(forms.Form):
    username = forms.CharField(label='Usuario')
    password = forms.CharField(label='Contraseña', widget=forms.PasswordInput)
    dni = forms.CharField(label='DNI')
    nombre_legal = forms.CharField(label='Nombre legal')
    nombre_mostrado = forms.CharField(label='Nombre a mostrar')
    telefono = forms.CharField(label='Teléfono', required=False)
    email_contacto = forms.EmailField(label='Email de contacto', required=False)

    def clean_username(self):
        username = self.cleaned_data['username']
        User = get_user_model()
        if User.objects.filter(username=username).exists():
            raise ValidationError('Ya existe un usuario con ese nombre.')
        return username

    def clean_dni(self):
        dni = self.cleaned_data['dni']
        if Paciente.objects.filter(dni=dni).exists():
            raise ValidationError('Ya existe un paciente con ese DNI.')
        return dni

    def save(self):
        User = get_user_model()
        user = User.objects.create_user(
            username=self.cleaned_data['username'],
            password=self.cleaned_data['password'],
            first_name=self.cleaned_data['nombre_mostrado'],
            email=self.cleaned_data['email_contacto'],
        )
        paciente = Paciente.objects.create(
            user=user,
            dni=self.cleaned_data['dni'],
            nombre_legal=self.cleaned_data['nombre_legal'],
            nombre_mostrado=self.cleaned_data['nombre_mostrado'],
            telefono=self.cleaned_data['telefono'],
            email_contacto=self.cleaned_data['email_contacto'],
        )
        return paciente


class PacienteUpdateForm(forms.ModelForm):
    class Meta:
        model = Paciente
        fields = ['dni', 'nombre_legal', 'nombre_mostrado', 'telefono', 'email_contacto']


class UsuarioUpdateForm(forms.ModelForm):
    class Meta:
        model = get_user_model()
        fields = ['first_name', 'last_name', 'email']
        labels = {
            'first_name': 'Nombre',
            'last_name': 'Apellidos',
            'email': 'Email',
        }
