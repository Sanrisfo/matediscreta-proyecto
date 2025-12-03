from django.db import models
from usuarios.models import Turista
from lugares.models import Destino
from datetime import datetime, timedelta
from decimal import Decimal
import re
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
        Calcula y actualiza los totales del itinerario:
        - costo_total: suma de costos REALES de las actividades
        - tiempo_total_minutos: suma de duraciones REALES
        - distancia_total_km: estimación basada en número de destinos
        
        CORREGIDO: Ahora extrae los costos de las notas si están disponibles
        """
        items = self.items.all().select_related('destino')
        
        costo_total = Decimal('0.00')
        tiempo_total = 0
        destinos_unicos = set()
        
        for item in items:
            # Registrar destino único
            destinos_unicos.add(item.destino.id)
            
            # CALCULAR TIEMPO: Diferencia entre hora_inicio y hora_fin
            if item.hora_inicio and item.hora_fin:
                inicio_dt = datetime.combine(datetime.today(), item.hora_inicio)
                fin_dt = datetime.combine(datetime.today(), item.hora_fin)
                
                # Manejar casos donde hora_fin es al día siguiente
                if fin_dt < inicio_dt:
                    fin_dt += timedelta(days=1)
                
                duracion_minutos = (fin_dt - inicio_dt).seconds / 60
                tiempo_total += int(duracion_minutos)
            
            # CALCULAR COSTO: Intentar extraer de las notas primero
            costo_item = None
            
            # Intentar parsear el costo de las notas (formato: "💰 Costo: S/ 50.00")
            if item.notas and 'Costo:' in item.notas:
                try:
                    # Buscar el patrón "S/ XX.XX" en las notas
                    import re
                    match = re.search(r'S/\s*(\d+\.?\d*)', item.notas)
                    if match:
                        costo_item = Decimal(match.group(1))
                except:
                    pass
            
            # Si no se pudo extraer, usar costo del destino
            if costo_item is None:
                costo_item = item.destino.costo_entrada
            
            costo_total += costo_item
        
        # Estimar distancia (5km entre cada destino)
        num_destinos = len(destinos_unicos)
        distancia_estimada = Decimal(str((num_destinos - 1) * 5)) if num_destinos > 1 else Decimal('0.00')
        
        # Actualizar campos
        self.costo_total = costo_total
        self.tiempo_total_minutos = tiempo_total
        self.distancia_total_km = distancia_estimada
        self.save(update_fields=['costo_total', 'tiempo_total_minutos', 'distancia_total_km'])


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