from django.db import models
from itinerarios.models import Itinerario
import uuid

class Ticket(models.Model):
    """
    Ticket electrónico con código QR
    """
    ESTADO_CHOICES = [
        ('activo', 'Activo'),
        ('usado', 'Usado'),
        ('vencido', 'Vencido'),
        ('cancelado', 'Cancelado'),
    ]
    
    itinerario = models.OneToOneField(Itinerario, on_delete=models.CASCADE, related_name='ticket')
    
    # Identificador único
    codigo = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    codigo_qr = models.ImageField(upload_to='tickets/qr/', blank=True, null=True)
    
    fecha_emision = models.DateTimeField(auto_now_add=True)
    fecha_validez = models.DateField(help_text="Fecha hasta la cual es válido el ticket")
    
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='activo')
    
    # Validación
    fecha_uso = models.DateTimeField(null=True, blank=True)
    validado_por = models.CharField(max_length=200, blank=True, help_text="Usuario/sistema que validó")
    
    class Meta:
        verbose_name = "Ticket"
        verbose_name_plural = "Tickets"
        ordering = ['-fecha_emision']
    
    def __str__(self):
        return f"Ticket {self.codigo} - {self.itinerario.nombre}"
    
    def generar_qr(self):
        """
        TODO: Implementar generación de código QR
        Usar librería qrcode para generar imagen
        """
        pass
    
    def validar(self, validador):
        """
        TODO: Marcar ticket como usado
        """
        pass


print("✅ Modelos creados para todas las apps")
print("\n📝 Incluye:")
print("   - usuarios.Turista (usuario con preferencias)")
print("   - lugares.Destino, Categoria, Actividad, ImagenDestino")
print("   - rutas.Ruta (grafo de conexiones)")
print("   - itinerarios.Itinerario, ItemItinerario")
print("   - tickets.Ticket (con QR)")