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
        rutas = Ruta.objects.filter(activo=True).select_related('origen', 'destino')
        
        for ruta in rutas:
            # Grafo dirigido: origen -> destino
            self.grafo[ruta.origen.id].append({
                'destino_id': ruta.destino.id,
                'peso': float(ruta.distancia_km),  # Puedes usar distancia o tiempo
                'tiempo': ruta.tiempo_minutos,
                'costo': float(ruta.costo_transporte),
            })
    
    def dijkstra(self, origen_id, destino_id):
        """
        Algoritmo de Dijkstra para encontrar la ruta más corta
        
        TODO: Implementar el algoritmo completo
        Retorna: (distancia_total, path)
        
        Pasos:
        1. Inicializar distancias a infinito excepto origen (0)
        2. Usar cola de prioridad (heap)
        3. Recorrer vecinos y actualizar distancias
        4. Reconstruir el path
        """
        
        # Placeholder
        distancias = {origen_id: 0}
        anteriores = {}
        visitados = set()
        cola = [(0, origen_id)]
        
        # TODO: Implementar lógica de Dijkstra aquí
        
        return None, []
    
    def calcular_rutas_multiples(self, lista_destinos):
        """
        Calcular ruta óptima visitando múltiples destinos
        
        TODO: Problema del viajante (TSP simplificado)
        Usar heurística o fuerza bruta para listas pequeñas
        """
        pass