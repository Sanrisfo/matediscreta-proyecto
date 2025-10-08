from django.db import models
from lugares.models import Destino

class Ruta(models.Model):
    """
    Conexiones entre destinos (grafo)
    Representa aristas en el grafo de destinos
    """
    MEDIO_TRANSPORTE_CHOICES = [
        ('caminando', 'Caminando'),
        ('auto', 'Auto'),
        ('bus', 'Bus'),
        ('taxi', 'Taxi'),
        ('bicicleta', 'Bicicleta'),
    ]
    
    origen = models.ForeignKey(Destino, on_delete=models.CASCADE, related_name='rutas_desde')
    destino = models.ForeignKey(Destino, on_delete=models.CASCADE, related_name='rutas_hacia')
    
    distancia_km = models.DecimalField(max_digits=6, decimal_places=2)
    tiempo_minutos = models.IntegerField()
    medio_transporte = models.CharField(max_length=20, choices=MEDIO_TRANSPORTE_CHOICES)
    costo_transporte = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    
    activo = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = "Ruta"
        verbose_name_plural = "Rutas"
        unique_together = ['origen', 'destino', 'medio_transporte']
    
    def __str__(self):
        return f"{self.origen.nombre} → {self.destino.nombre} ({self.medio_transporte})"

