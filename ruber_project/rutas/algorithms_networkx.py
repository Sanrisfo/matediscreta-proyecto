# rutas/algorithms_networkx.py

import math
import networkx as nx
from rutas.models import Destino

def haversine(lat1, lon1, lat2, lon2):
    R = 6371  # km
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = math.sin(dlat/2)**2 + math.cos(lat1)*math.cos(lat2)*math.sin(dlon/2)**2
    return 2 * R * math.asin(math.sqrt(a))


def build_graph_networkx():
    G = nx.Graph()

    # Crear nodos desde Destino
    for dest in Destino.objects.all():
        G.add_node(
            dest.id,
            lat=float(dest.latitud),
            lon=float(dest.longitud)
        )

    destinos = list(Destino.objects.all())

    # Crear aristas por distancia real (KNN o fully connected si prefieres)
    for i in range(len(destinos)):
        for j in range(i+1, len(destinos)):
            d1 = destinos[i]
            d2 = destinos[j]

            distancia = haversine(
                float(d1.latitud),
                float(d1.longitud),
                float(d2.latitud),
                float(d2.longitud)
            )

            G.add_edge(d1.id, d2.id, weight=distancia)

    return G


def dijkstra_networkx(lat_origen, lon_origen, destino_id):
    G = build_graph_networkx()

    origen_usuario = "user"
    G.add_node(origen_usuario, lat=lat_origen, lon=lon_origen)

    for nodo, data in G.nodes(data=True):
        if nodo == origen_usuario:
            continue

        distancia = haversine(
            lat_origen, lon_origen,
            data['lat'], data['lon']
        )
        G.add_edge(origen_usuario, nodo, weight=distancia)

    try:
        dist = nx.dijkstra_path_length(G, origen_usuario, destino_id, weight="weight")
        camino = nx.dijkstra_path(G, origen_usuario, destino_id, weight="weight")
    except Exception:
        return float('inf'), []

    # Convertir IDs a coordenadas reales
    destinos = Destino.objects.in_bulk([n for n in camino if n != "user"])

    path = []
    for n in camino:
        if n == "user":
            path.append({
                'id': 'user',
                'nombre': 'Tú',
                'lat': lat_origen,
                'lng': lon_origen
            })
        else:
            dest = destinos[n]
            path.append({
                'id': dest.id,
                'nombre': dest.nombre,
                'lat': float(dest.latitud),
                'lng': float(dest.longitud)
            })

    return dist, path
