from django.contrib.auth.models import AbstractUser
from django.db import models

class Turista(AbstractUser):
    """
    Usuario extendido con preferencias turísticas
    """
    PREFERENCIAS_CHOICES = [
        ('playa', 'Playero'),
        ('gastronomia', 'Gastronomía Local'),
        ('museos', 'Museos y Cultura'),
        ('aventura', 'Aventura y Deportes'),
        ('naturaleza', 'Naturaleza'),
        ('vida_nocturna', 'Vida Nocturna'),
        ('compras', 'Compras'),
        ('relax', 'Relax y Spa'),
    ]
    
    telefono = models.CharField(max_length=20, blank=True, null=True)
    pais_origen = models.CharField(max_length=100, blank=True, null=True)
    foto_perfil = models.ImageField(upload_to='usuarios/perfiles/', blank=True, null=True)
    
    # Preferencias (se pueden seleccionar múltiples)
    preferencias = models.JSONField(default=list, blank=True)
    
    # Restricciones de viaje
    presupuesto_max = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    tiempo_disponible_dias = models.IntegerField(null=True, blank=True, help_text="Días disponibles para el viaje")
    
    fecha_registro = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Turista"
        verbose_name_plural = "Turistas"
    
    def __str__(self):
        return self.get_full_name() or self.username
    
    def get_preferencias_display(self):
        """Retorna las preferencias en formato legible"""
        preferencias_dict = dict(self.PREFERENCIAS_CHOICES)
        return [preferencias_dict.get(p, p) for p in self.preferencias]