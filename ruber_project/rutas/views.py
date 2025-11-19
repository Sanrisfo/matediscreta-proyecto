from django.shortcuts import render
from django.http import JsonResponse # Importante para responder a AJAX
from .models import Ruta
from lugares.models import Destino
from .algorithms import GrafoRutas # Importamos nuestra clase

def mapa_rutas(request):
    """
    Visualización de rutas en mapa interactivo y cálculo Dijkstra
    """
    # Si es una petición AJAX (cálculo de ruta)
    if request.headers.get('x-requested-with') == 'XMLHttpRequest' and request.GET.get('origen'):
        origen_id = int(request.GET.get('origen'))
        destino_id = int(request.GET.get('destino'))
        
        grafo = GrafoRutas()
        distancia, camino_ids = grafo.dijkstra(origen_id, destino_id)
        
        if camino_ids:
            # Recuperar los objetos Destino en orden
            # Nota: Hacemos esto para obtener lat/lng de cada punto del camino
            destinos_camino = []
            for id_nodo in camino_ids:
                destinos_camino.append(Destino.objects.get(id=id_nodo))
            
            data = {
                'success': True,
                'distancia': distancia,
                'path': [{'lat': float(d.latitud), 'lng': float(d.longitud), 'nombre': d.nombre} for d in destinos_camino]
            }
        else:
            data = {'success': False, 'error': 'No se encontró ruta entre estos destinos'}
            
        return JsonResponse(data)

    # Vista normal (GET inicial)
    destinos = Destino.objects.filter(activo=True)
    rutas = Ruta.objects.filter(activo=True)
    
    destinos_json = list(destinos.values('id', 'nombre', 'latitud', 'longitud'))
    rutas_json = list(rutas.values('origen_id', 'destino_id', 'distancia_km', 'tiempo_minutos'))
    
    context = {
        'destinos': destinos,
        'rutas': rutas,
        'destinos_json': destinos_json,
        'rutas_json': rutas_json,
    }
    return render(request, 'rutas/mapa_rutas.html', context)