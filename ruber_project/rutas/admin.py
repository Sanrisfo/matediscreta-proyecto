from django.contrib import admin
from .models import Ruta

@admin.register(Ruta)
class RutaAdmin(admin.ModelAdmin):
    list_display = ['origen', 'destino', 'medio_transporte', 'distancia_km', 'tiempo_minutos', 'activo']
    list_filter = ['medio_transporte', 'activo']
    search_fields = ['origen__nombre', 'destino__nombre']
    list_editable = ['activo']
    
    fieldsets = (
        ('Conexión', {
            'fields': ('origen', 'destino')
        }),
        ('Detalles de la Ruta', {
            'fields': ('distancia_km', 'tiempo_minutos', 'medio_transporte', 'costo_transporte')
        }),
        ('Estado', {
            'fields': ('activo',)
        }),
    )