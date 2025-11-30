from collections import defaultdict
from .models import Destino, Actividad
import heapq


class GrafoRecomendaciones:
    
    def __init__(self):
      
        self.grafo = defaultdict(list)
        self.destinos_cache = {}
    
    def construir_grafo(self, destinos_queryset=None):
     
        # Obtener todos los destinos activos
        if destinos_queryset is None:
            destinos = list(Destino.objects.filter(activo=True).prefetch_related('actividades'))
        else:
            destinos = list(destinos_queryset)
        
        # Cachear destinos por ID para acceso rápido
        self.destinos_cache = {d.id: d for d in destinos}
        
        # Construir aristas entre todos los pares de destinos
        for i, destino1 in enumerate(destinos):
            for destino2 in destinos[i+1:]:  # Evitar duplicados y auto-comparación
                peso = self._calcular_similitud(destino1, destino2)
                
                # Solo agregar aristas con similitud significativa (> 0.1)
                if peso > 0.1:
                    # Grafo no dirigido: agregar en ambas direcciones
                    self.grafo[destino1.id].append((destino2.id, peso))
                    self.grafo[destino2.id].append((destino1.id, peso))
        
        print(f"Grafo construido con {len(destinos)} nodos")
        print(f"Total de aristas: {sum(len(v) for v in self.grafo.values()) // 2}")
    
    def _calcular_similitud(self, destino1, destino2):
      
        peso_total = 0.0
        
        # ===================================
        # 1. SIMILITUD POR CATEGORÍA (40%)
        # ===================================
        if destino1.categoria and destino2.categoria:
            if destino1.categoria_id == destino2.categoria_id:
                peso_categoria = 1.0
            else:
                peso_categoria = 0.0
        else:
            peso_categoria = 0.0
        
        peso_total += 0.4 * peso_categoria
        
        # ===================================
        # 2. SIMILITUD POR TAGS (40%)
        # ===================================
        tags1 = set(destino1.tags_preferencias or [])
        tags2 = set(destino2.tags_preferencias or [])
        
        if tags1 and tags2:
            # Coeficiente de Jaccard: |A ∩ B| / |A ∪ B|
            interseccion = len(tags1 & tags2)
            union = len(tags1 | tags2)
            peso_tags = interseccion / union if union > 0 else 0.0
        else:
            peso_tags = 0.0
        
        peso_total += 0.4 * peso_tags
        
        # ===================================
        # 3. SIMILITUD POR ACTIVIDADES (20%)
        # ===================================
        tipos1 = set(act.tipo for act in destino1.actividades.all())
        tipos2 = set(act.tipo for act in destino2.actividades.all())
        
        if tipos1 and tipos2:

            # Coeficiente de Jaccard
            interseccion = len(tipos1 & tipos2)
            union = len(tipos1 | tipos2)
            peso_actividades = interseccion / union if union > 0 else 0.0
        else:
            peso_actividades = 0.0
        
        peso_total += 0.2 * peso_actividades
        
        return peso_total
    
    def recomendar(self, destino_id, n=5):
    
        if destino_id not in self.grafo:
            print(f"Destino {destino_id} no está en el grafo")
            return []
        
        vecinos = self.grafo[destino_id]
        
        if not vecinos:
            print(f"⚠ No hay vecinos para destino {destino_id}")
            return []
        
        top_n = heapq.nlargest(n, vecinos, key=lambda x: x[1])
        
        recomendaciones = []
        for destino_vecino_id, peso in top_n:
            destino_obj = self.destinos_cache.get(destino_vecino_id)
            if destino_obj:
                recomendaciones.append((destino_obj, peso))
        
        print(f"✓ Generadas {len(recomendaciones)} recomendaciones para destino {destino_id}")
        return recomendaciones
    
    def obtener_estadisticas(self, destino_id):
        
        if destino_id not in self.grafo:
            return None
        
        vecinos = self.grafo[destino_id]
        pesos = [peso for _, peso in vecinos]
        
        return {
            'num_conexiones': len(vecinos),
            'peso_promedio': sum(pesos) / len(pesos) if pesos else 0,
            'peso_maximo': max(pesos) if pesos else 0,
            'peso_minimo': min(pesos) if pesos else 0,
        }



def obtener_recomendaciones(destino_actual, n=5):
   
    grafo = GrafoRecomendaciones() #CONSTRUCTOR
    grafo.construir_grafo() #METODO APLICADO SOBRE NUESTRA BASE DE DATOS
    
    #Variable donde se almacena
    recomendaciones = grafo.recomendar(destino_actual.id, n)
    
    recomendaciones_con_porcentaje = [
        (destino, peso, int(peso * 100))
        for destino, peso in recomendaciones
    ]
    
    return recomendaciones_con_porcentaje

