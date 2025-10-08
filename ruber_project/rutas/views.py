from django.shortcuts import render
from .models import Ruta
from lugares.models import Destino

def mapa_rutas(request):
    """
    Visualización de rutas en mapa interactivo
    """
    destinos = Destino.objects.filter(activo=True)
    rutas = Ruta.objects.filter(activo=True)
    
    # Preparar datos para el mapa (formato JSON)
    destinos_json = list(destinos.values('id', 'nombre', 'latitud', 'longitud'))
    rutas_json = list(rutas.values('origen_id', 'destino_id', 'distancia_km', 'tiempo_minutos'))
    
    context = {
        'destinos': destinos,
        'rutas': rutas,
        'destinos_json': destinos_json,
        'rutas_json': rutas_json,
    }
    return render(request, 'rutas/mapa_rutas.html', context)