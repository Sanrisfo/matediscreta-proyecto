from django.contrib import admin
from .models import Itinerario, ItemItinerario

class ItemItinerarioInline(admin.TabularInline):
    model = ItemItinerario
    extra = 1
    ordering = ['orden']


@admin.register(Itinerario)
class ItinerarioAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'turista', 'fecha_inicio', 'fecha_fin', 'estado', 'costo_total']
    list_filter = ['estado', 'fecha_creacion']
    search_fields = ['nombre', 'turista__username']
    inlines = [ItemItinerarioInline]
    
    fieldsets = (
        ('Información General', {
            'fields': ('turista', 'nombre', 'descripcion', 'estado')
        }),
        ('Fechas', {
            'fields': ('fecha_inicio', 'fecha_fin')
        }),
        ('Totales Calculados', {
            'fields': ('costo_total', 'tiempo_total_minutos', 'distancia_total_km'),
            'description': 'Estos valores se calculan automáticamente'
        }),
    )


@admin.register(ItemItinerario)
class ItemItinerarioAdmin(admin.ModelAdmin):
    list_display = ['itinerario', 'destino', 'dia', 'orden', 'hora_inicio', 'hora_fin']
    list_filter = ['dia', 'itinerario']
    search_fields = ['destino__nombre', 'itinerario__nombre']