from django.contrib import admin
from .models import Categoria, Destino, Actividad, ImagenDestino

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'icono']
    search_fields = ['nombre']


class ActividadInline(admin.TabularInline):
    model = Actividad
    extra = 1


class ImagenDestinoInline(admin.TabularInline):
    model = ImagenDestino
    extra = 1


@admin.register(Destino)
class DestinoAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'categoria', 'calificacion', 'costo_entrada', 'activo']
    list_filter = ['categoria', 'activo', 'calificacion']
    search_fields = ['nombre', 'descripcion']
    list_editable = ['activo']
    inlines = [ActividadInline, ImagenDestinoInline]
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('nombre', 'descripcion', 'categoria', 'imagen_principal')
        }),
        ('Ubicación', {
            'fields': ('latitud', 'longitud', 'direccion')
        }),
        ('Detalles', {
            'fields': ('costo_entrada', 'tiempo_visita_estimado', 'calificacion', 'tags_preferencias')
        }),
        ('Estado', {
            'fields': ('activo',)
        }),
    )


@admin.register(Actividad)
class ActividadAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'destino', 'tipo', 'costo', 'duracion_minutos', 'disponible']
    list_filter = ['tipo', 'disponible', 'destino']
    search_fields = ['nombre', 'descripcion']