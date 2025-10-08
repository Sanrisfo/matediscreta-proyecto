from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

class Categoria(models.Model):
    """
    Categorías de destinos turísticos
    """
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True)
    icono = models.CharField(max_length=50, blank=True, help_text="Clase CSS para icono")
    
    class Meta:
        verbose_name = "Categoría"
        verbose_name_plural = "Categorías"
    
    def __str__(self):
        return self.nombre


class Destino(models.Model):
    """
    Lugares turísticos disponibles
    """
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField()
    categoria = models.ForeignKey(Categoria, on_delete=models.SET_NULL, null=True, related_name='destinos')
    
    # Ubicación
    latitud = models.DecimalField(max_digits=9, decimal_places=6)
    longitud = models.DecimalField(max_digits=9, decimal_places=6)
    direccion = models.CharField(max_length=255, blank=True)
    
    # Información adicional
    costo_entrada = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    tiempo_visita_estimado = models.IntegerField(help_text="Tiempo estimado en minutos")
    
    # Preferencias asociadas
    tags_preferencias = models.JSONField(default=list, blank=True, 
                                         help_text="Tags: playa, museos, gastronomia, etc.")
    
    # Calificación
    calificacion = models.DecimalField(max_digits=3, decimal_places=2, 
                                       validators=[MinValueValidator(0), MaxValueValidator(5)],
                                       default=0.00)
    
    # Media
    imagen_principal = models.ImageField(upload_to='destinos/', blank=True, null=True)
    
    activo = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Destino"
        verbose_name_plural = "Destinos"
        ordering = ['-calificacion', 'nombre']
    
    def __str__(self):
        return self.nombre


class Actividad(models.Model):
    """
    Actividades disponibles en cada destino
    """
    TIPO_CHOICES = [
        ('visita_guiada', 'Visita Guiada'),
        ('degustacion', 'Degustación'),
        ('deporte', 'Deporte/Aventura'),
        ('cultural', 'Cultural'),
        ('entretenimiento', 'Entretenimiento'),
    ]
    
    destino = models.ForeignKey(Destino, on_delete=models.CASCADE, related_name='actividades')
    nombre = models.CharField(max_length=200)
    tipo = models.CharField(max_length=50, choices=TIPO_CHOICES)
    descripcion = models.TextField()
    costo = models.DecimalField(max_digits=8, decimal_places=2)
    duracion_minutos = models.IntegerField()
    
    disponible = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = "Actividad"
        verbose_name_plural = "Actividades"
    
    def __str__(self):
        return f"{self.nombre} - {self.destino.nombre}"


class ImagenDestino(models.Model):
    """
    Galería de imágenes para cada destino
    """
    destino = models.ForeignKey(Destino, on_delete=models.CASCADE, related_name='imagenes')
    imagen = models.ImageField(upload_to='destinos/galeria/')
    descripcion = models.CharField(max_length=255, blank=True)
    orden = models.IntegerField(default=0)
    
    class Meta:
        verbose_name = "Imagen de Destino"
        verbose_name_plural = "Imágenes de Destinos"
        ordering = ['orden']
    
    def __str__(self):
        return f"Imagen {self.orden} - {self.destino.nombre}"