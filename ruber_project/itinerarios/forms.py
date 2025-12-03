from django import forms
from .models import ItemItinerario

class GenerarItinerarioForm(forms.Form):
    """
    Formulario simplificado para generar itinerario
    Ahora solo pide nombre y fechas (preferencias y presupuesto vienen del perfil)
    """
    nombre = forms.CharField(
        max_length=200,
        label="Nombre del itinerario",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ej: Mi viaje a Cusco 2025'
        })
    )
    fecha_inicio = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        label="Fecha de inicio"
    )
    fecha_fin = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        label="Fecha de fin"
    )
    
    def clean(self):
        cleaned_data = super().clean()
        fecha_inicio = cleaned_data.get('fecha_inicio')
        fecha_fin = cleaned_data.get('fecha_fin')
        
        if fecha_inicio and fecha_fin:
            if fecha_fin < fecha_inicio:
                raise forms.ValidationError(
                    'La fecha de fin no puede ser anterior a la fecha de inicio'
                )
        
        return cleaned_data


class EditarItemForm(forms.ModelForm):
    """
    Formulario para editar día y hora de un item del itinerario
    """
    class Meta:
        model = ItemItinerario
        fields = ['dia', 'hora_inicio', 'hora_fin']
        widgets = {
            'dia': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'placeholder': 'Día del itinerario'
            }),
            'hora_inicio': forms.TimeInput(attrs={
                'type': 'time',
                'class': 'form-control'
            }),
            'hora_fin': forms.TimeInput(attrs={
                'type': 'time',
                'class': 'form-control'
            }),
        }
        labels = {
            'dia': 'Día del itinerario',
            'hora_inicio': 'Hora de inicio',
            'hora_fin': 'Hora de fin'
        }
    
    def clean(self):
        cleaned_data = super().clean()
        hora_inicio = cleaned_data.get('hora_inicio')
        hora_fin = cleaned_data.get('hora_fin')
        
        if hora_inicio and hora_fin:
            if hora_fin <= hora_inicio:
                raise forms.ValidationError(
                    'La hora de fin debe ser posterior a la hora de inicio'
                )
        
        return cleaned_data


class AgregarActividadForm(forms.Form):
    """
    Formulario para agregar una actividad a un itinerario existente
    """
    itinerario = forms.ChoiceField(
        label="Selecciona un itinerario",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    def __init__(self, usuario, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Cargar solo itinerarios activos del usuario
        from .models import Itinerario
        itinerarios = Itinerario.objects.filter(
            turista=usuario,
            estado__in=['borrador', 'confirmado']
        ).order_by('-fecha_creacion')
        
        self.fields['itinerario'].choices = [
            (it.id, f"{it.nombre} ({it.fecha_inicio.strftime('%d/%m/%Y')})")
            for it in itinerarios
        ]
        
        if not itinerarios.exists():
            self.fields['itinerario'].choices = [('', 'No tienes itinerarios activos')]
            self.fields['itinerario'].widget.attrs['disabled'] = True