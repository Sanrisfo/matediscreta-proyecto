from django.db import models
from usuarios.models import Turista
from lugares.models import Destino

class Itinerario(models.Model):
    """
    Plan de viaje generado para un turista
    """
    ESTADO_CHOICES = [
        ('borrador', 'Borrador'),
        ('confirmado', 'Confirmado'),
        ('en_proceso', 'En Proceso'),
        ('completado', 'Completado'),
        ('cancelado', 'Cancelado'),
    ]
    
    turista = models.ForeignKey(Turista, on_delete=models.CASCADE, related_name='itinerarios')
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True)
    
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    
    # Cálculos automáticos
    costo_total = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    tiempo_total_minutos = models.IntegerField(default=0)
    distancia_total_km = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='borrador')
    
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Itinerario"
        verbose_name_plural = "Itinerarios"
        ordering = ['-fecha_creacion']
    
    def __str__(self):
        return f"{self.nombre} - {self.turista.username}"
    
    def calcular_totales(self):
        """
        TODO: Implementar cálculo de costos, tiempo y distancia total
        Debe recorrer todos los items del itinerario y sumar
        """
        pass


class ItemItinerario(models.Model):
    """
    Cada parada en el itinerario
    """
    itinerario = models.ForeignKey(Itinerario, on_delete=models.CASCADE, related_name='items')
    destino = models.ForeignKey(Destino, on_delete=models.CASCADE)
    
    orden = models.IntegerField()
    dia = models.IntegerField(help_text="Día del itinerario (1, 2, 3...)")
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()
    
    notas = models.TextField(blank=True)
    
    class Meta:
        verbose_name = "Item de Itinerario"
        verbose_name_plural = "Items de Itinerario"
        ordering = ['itinerario', 'orden']
        unique_together = ['itinerario', 'orden']
    
    def __str__(self):
        return f"Día {self.dia} - {self.destino.nombre}"
