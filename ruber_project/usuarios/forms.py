from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import Turista

class RegistroForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=True, label="Nombre")
    last_name = forms.CharField(max_length=30, required=True, label="Apellido")
    
    class Meta:
        model = Turista
        fields = ['username', 'email', 'first_name', 'last_name', 'password1', 'password2']


class LoginForm(AuthenticationForm):
    username = forms.CharField(label="Usuario o Email")
    password = forms.CharField(label="Contraseña", widget=forms.PasswordInput)


class PerfilForm(forms.ModelForm):
    class Meta:
        model = Turista
        fields = ['first_name', 'last_name', 'email', 'telefono', 'pais_origen', 
                  'foto_perfil', 'preferencias', 'presupuesto_max', 'tiempo_disponible_dias']
        widgets = {
            'preferencias': forms.CheckboxSelectMultiple(choices=Turista.PREFERENCIAS_CHOICES),
        }