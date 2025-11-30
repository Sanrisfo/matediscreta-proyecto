from django import forms
from usuarios.models import Turista

class GenerarItinerarioForm(forms.Form):
    fecha_inicio = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        label="Fecha de inicio"
    )
    fecha_fin = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        label="Fecha de fin"
    )
    preferencias = forms.MultipleChoiceField(
        choices=Turista.PREFERENCIAS_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        label="Preferencias de viaje"
    )
    presupuesto_max = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        label="Presupuesto máximo",
        required=False
    )
