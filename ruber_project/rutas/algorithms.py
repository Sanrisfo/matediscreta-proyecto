import heapq
from collections import defaultdict
from .models import Ruta

class GrafoRutas:
    """
    Clase para manejar el grafo de rutas y aplicar algoritmos
    """
    
    def __init__(self):
        self.grafo = defaultdict(list)
        self.cargar_rutas()
    
    def cargar_rutas(self):
        """
        Cargar todas las rutas activas en la estructura de grafo
        """
        # Obtenemos las rutas activas de la BD
        rutas = Ruta.objects.filter(activo=True).select_related('origen', 'destino')
        
        for ruta in rutas:
            # Construimos la lista de adyacencia
            # Grafo dirigido: origen -> destino
            self.grafo[ruta.origen.id].append({
                'destino_id': ruta.destino.id,
                'peso': float(ruta.distancia_km),     # Distancia para Dijkstra
                'tiempo': ruta.tiempo_minutos,        # Datos extra para mostrar
                'costo': float(ruta.costo_transporte),
            })
    
    def dijkstra(self, origen_id, destino_id):
        """
        Algoritmo de Dijkstra para encontrar la ruta más corta.
        Retorna: (distancia_total, lista_de_ids_del_camino)
        """
        
        # Cola de prioridad: almacena tuplas (costo_acumulado, nodo_actual)
        # Inicializamos con el nodo origen y costo 0
        cola = [(0, origen_id)]
        
        # Diccionarios para reconstruir el camino y guardar costos mínimos
        # Inicializamos el origen con costo 0
        costos_minimos = {origen_id: 0}
        
        # Para reconstruir el camino: nodo_hijo -> nodo_padre
        padres = {origen_id: None}
        
        visitados = set()

        while cola:
            # Extraemos el nodo con menor costo actual
            costo_actual, nodo_actual = heapq.heappop(cola)

            # Si ya visitamos este nodo (y encontramos un camino mejor antes), lo saltamos
            if nodo_actual in visitados:
                continue
            visitados.add(nodo_actual)

            # Si llegamos al destino, terminamos la búsqueda
            if nodo_actual == destino_id:
                break

            # Explorar vecinos
            # self.grafo[nodo_actual] devuelve la lista de conexiones
            for arista in self.grafo[nodo_actual]:
                vecino_id = arista['destino_id']
                peso_arista = arista['peso'] # Usamos distancia_km como peso
                
                nuevo_costo = costo_actual + peso_arista

                # Si encontramos un camino más corto hacia el vecino
                if vecino_id not in costos_minimos or nuevo_costo < costos_minimos[vecino_id]:
                    costos_minimos[vecino_id] = nuevo_costo
                    padres[vecino_id] = nodo_actual
                    heapq.heappush(cola, (nuevo_costo, vecino_id))

        # --- Reconstrucción del camino (Backtracking) ---
        camino = []
        nodo = destino_id
        
        # Verificamos si realmente llegamos al destino
        if destino_id not in costos_minimos:
            return None, [] # No hay ruta posible

        # Retrocedemos desde el destino hasta el origen usando el diccionario 'padres'
        while nodo is not None:
            camino.append(nodo)
            nodo = padres.get(nodo)
        
        # El camino está al revés (Destino -> Origen), lo invertimos
        return costos_minimos[destino_id], camino[::-1]
    
    def calcular_rutas_multiples(self, lista_destinos):
        """
        Calcular ruta óptima visitando múltiples destinos (Opcional)
        """
        pass