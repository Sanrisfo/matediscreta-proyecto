import json
from django.http import JsonResponse
from django.shortcuts import render
from django.core.serializers.json import DjangoJSONEncoder

from rutas.models import Destino
from rutas.algorithms_networkx import dijkstra_networkx

from django.views.decorators.csrf import csrf_exempt
def extraer_param(request):
    """
    Extrae latitud, longitud y destino_id desde:
    - GET params
    - POST JSON
    - POST form
    Retorna (lat, lon, destino_id) o (None, None, None)
    """

    # Intentar por GET
    lat = request.GET.get("lat") or request.GET.get("lat_origen")
    lon = request.GET.get("lon") or request.GET.get("lng") or request.GET.get("lng_origen")
    destino = request.GET.get("destino") or request.GET.get("destino_id")

    # Si GET ya dio los parámetros, regresamos
    if lat and lon and destino:
        return lat, lon, destino

    # Intentar por POST JSON
    if request.method == "POST":
        try:
            body = request.body.decode("utf-8")
            if body.strip():
                data = json.loads(body)
                lat = lat or data.get("lat") or data.get("lat_origen")
                lon = lon or data.get("lng") or data.get("lon") or data.get("lng_origen")
                destino = destino or data.get("destino") or data.get("destino_id")
        except Exception:
            pass

        # Intentar por POST form-encoded
        lat = lat or request.POST.get("lat") or request.POST.get("lat_origen")
        lon = lon or request.POST.get("lon") or request.POST.get("lng") or request.POST.get("lng_origen")
        destino = destino or request.POST.get("destino") or request.POST.get("destino_id")

    return lat, lon, destino

@csrf_exempt
def mapa_rutas(request):
    """
    Vista principal del mapa.
    - Si llegan parámetros lat/lon/destino → calcula ruta (API)
    - Si no → renderiza la página del mapa
    """

    # Intentar extraer parámetros desde GET o POST
    lat, lon, destino_id = extraer_param(request)

    # Si recibimos parámetros → se trata de una petición API
    if lat and lon and destino_id:
        try:
            lat = float(lat)
            lon = float(lon)
            destino_id = int(destino_id)
        except ValueError:
            return JsonResponse({
                'success': False,
                'error': 'Parámetros no numéricos.'
            })

        # Ejecutar el algoritmo
        try:
            distancia, ruta = dijkstra_networkx(lat, lon, destino_id)
        except Exception as e:
            print("Error ejecutando Dijkstra:", e)
            return JsonResponse({
                'success': False,
                'error': f'Error interno: {e}'
            })

        if not ruta or distancia == float("inf"):
            return JsonResponse({
                'success': False,
                'error': 'No se pudo encontrar una ruta válida.'
            })

        return JsonResponse({
            'success': True,
            'distancia_km': round(distancia, 2),
            'ruta': ruta
        })

    # ---------------------------
    #  Petición normal → renderizar mapa
    # ---------------------------
    destinos = list(Destino.objects.values(
        'id', 'nombre', 'latitud', 'longitud'
    ))

    context = {
        'destinos': destinos,
        'destinos_json': json.dumps(destinos, ensure_ascii=False, cls=DjangoJSONEncoder),
    }

    return render(request, 'rutas/mapa_rutas.html', context)
