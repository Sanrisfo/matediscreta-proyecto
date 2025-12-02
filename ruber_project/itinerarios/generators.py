from datetime import timedelta, time, datetime
from decimal import Decimal
from lugares.models import Destino, Actividad
from .models import Itinerario, ItemItinerario
from django.db.models import Q, Count, Avg
import heapq
from collections import defaultdict
from itertools import combinations

class GeneradorItinerarios:
    """
    Generador de itinerarios usando Matemática Discreta:
    - Teoría de Conjuntos (filtrado por preferencias)
    - Combinatoria (selección óptima de actividades)
    - Grafos (Dijkstra para rutas óptimas)
    - Optimización (función de scoring multi-criterio)
    """
    
    # Constantes para ponderación
    PESO_CALIFICACION = 0.4
    PESO_PREFERENCIA = 0.35
    PESO_COSTO = 0.15
    PESO_POPULARIDAD = 0.1
    
    # Tiempos promedio (en minutos)
    TIEMPO_PROMEDIO_ACTIVIDAD = 90
    TIEMPO_BUFFER = 30  # tiempo entre actividades
    HORAS_PRODUCTIVAS_DIA = 10  # 10 horas de turismo por día
    
    def __init__(self, turista):
        self.turista = turista
        self.grafo_rutas = {}  # Para Dijkstra
        
    def generar(self, fecha_inicio, fecha_fin, preferencias, presupuesto_max=None):
        """
        Genera un itinerario óptimo usando algoritmos de optimización
        
        Pasos:
        1. Filtrar destinos por intersección de conjuntos (preferencias)
        2. Calcular scoring de cada destino
        3. Seleccionar combinación óptima de destinos (combinatoria)
        4. Para cada destino, seleccionar actividades óptimas
        5. Ordenar destinos usando Dijkstra (ruta más corta)
        6. Distribuir en días respetando restricciones de tiempo
        """
        
        # Asegurar que preferencias sea una lista
        if isinstance(preferencias, str):
            preferencias = [p.strip() for p in preferencias.split(',') if p.strip()]
        elif not isinstance(preferencias, list):
            preferencias = list(preferencias) if preferencias else []
        
        # Calcular días disponibles
        dias_totales = (fecha_fin - fecha_inicio).days + 1
        
        # 1. TEORÍA DE CONJUNTOS: Filtrar destinos por preferencias
        destinos_candidatos = self._filtrar_destinos_por_preferencias(
            preferencias, 
            presupuesto_max
        )
        
        if not destinos_candidatos:
            # Crear itinerario vacío si no hay coincidencias
            return self._crear_itinerario_vacio(fecha_inicio, fecha_fin)
        
        # 2. SCORING: Calcular puntuación de cada destino
        destinos_con_score = self._calcular_scores(
            destinos_candidatos, 
            preferencias, 
            presupuesto_max
        )
        
        # 3. COMBINATORIA: Seleccionar mejor combinación de destinos
        destinos_seleccionados = self._seleccionar_destinos_optimos(
            destinos_con_score,
            dias_totales,
            presupuesto_max
        )
        
        # 4. Para cada destino, seleccionar actividades óptimas
        destinos_con_actividades = self._seleccionar_actividades_por_destino(
            destinos_seleccionados,
            preferencias,
            presupuesto_max
        )
        
        # 5. GRAFOS (DIJKSTRA): Ordenar destinos por ruta óptima
        destinos_ordenados = self._ordenar_destinos_dijkstra(destinos_con_actividades)
        
        # 6. Crear itinerario y distribuir en días
        itinerario = self._crear_itinerario(
            fecha_inicio, 
            fecha_fin, 
            destinos_ordenados,
            preferencias
        )
        
        return itinerario
    
    def _filtrar_destinos_por_preferencias(self, preferencias, presupuesto_max):
        """
        TEORÍA DE CONJUNTOS:
        Usa intersección de conjuntos para filtrar destinos
        
        Sea P = conjunto de preferencias del usuario
        Sea T_d = conjunto de tags del destino d
        
        Destino es candidato si: |P ∩ T_d| > 0
        """
        destinos = Destino.objects.filter(activo=True)
        
        # Filtrar por presupuesto
        if presupuesto_max:
            destinos = destinos.filter(costo_entrada__lte=presupuesto_max)
        
        # Filtrar por intersección de preferencias
        # Usando Q objects para OR de todas las preferencias
        if preferencias:
            filtro_tags = Q()
            for pref in preferencias:
                filtro_tags |= Q(tags_preferencias__icontains=pref)
            
            destinos = destinos.filter(filtro_tags).distinct()
        
        return list(destinos.prefetch_related('actividades'))
    
    def _calcular_scores(self, destinos, preferencias, presupuesto_max):
        """
        FUNCIÓN DE OPTIMIZACIÓN CORREGIDA
        """
        destinos_con_score = []
        max_actividades = max([d.actividades.count() for d in destinos]) if destinos else 1
        
        for destino in destinos:
            # Componente 1: Calificación
            calificacion_valor = float(destino.calificacion) if destino.calificacion else 3.0
            score_calificacion = calificacion_valor / 5.0
            
            # Componente 2: Match de preferencias (CORREGIDO)
            # ---------------------------------------------------------
            raw_tags = destino.tags_preferencias or []
            
            # Validación inteligente: ¿Es Texto o es Lista?
            if isinstance(raw_tags, str):
                # Si es texto "museo,arte", lo cortamos
                lista_tags = raw_tags.split(',')
            elif isinstance(raw_tags, list):
                # Si ya es lista ['museo', 'arte'], la usamos tal cual
                lista_tags = raw_tags
            else:
                lista_tags = []

            tags_destino = set([str(tag).strip().lower() for tag in lista_tags])
            # ---------------------------------------------------------

            preferencias_set = set([p.lower() for p in preferencias])
            interseccion = tags_destino & preferencias_set
            
            score_preferencias = len(interseccion) / len(preferencias) if preferencias else 0.5
            
            # Componente 3: Costo
            if presupuesto_max and float(presupuesto_max) > 0:
                costo_destino = float(destino.costo_entrada) if destino.costo_entrada else 0.0
                score_costo = 1 - (costo_destino / float(presupuesto_max))
                score_costo = max(0.0, min(1.0, score_costo))
            else:
                score_costo = 0.5
            
            # Componente 4: Popularidad
            num_actividades = destino.actividades.count()
            score_popularidad = num_actividades / float(max_actividades) if max_actividades > 0 else 0.5
            
            # Score total
            score_total = (
                self.PESO_CALIFICACION * score_calificacion +
                self.PESO_PREFERENCIA * score_preferencias +
                self.PESO_COSTO * score_costo +
                self.PESO_POPULARIDAD * score_popularidad
            )
            
            destinos_con_score.append({
                'destino': destino,
                'score': score_total,
                'match_tags': len(interseccion),
                'num_actividades': num_actividades
            })
        
        destinos_con_score.sort(key=lambda x: x['score'], reverse=True)
        return destinos_con_score

    def _seleccionar_destinos_optimos(self, destinos_con_score, dias_totales, presupuesto_max):
        """
        PROBLEMA DE LA MOCHILA (Knapsack Problem):
        Seleccionar subconjunto de destinos que maximice valor (score)
        sujeto a restricciones de tiempo y presupuesto
        
        Enfoque: Greedy Algorithm (aproximación)
        - Ordenar por score (ya hecho)
        - Ir agregando destinos mientras quepan en tiempo y presupuesto
        """
        
        minutos_disponibles = dias_totales * self.HORAS_PRODUCTIVAS_DIA * 60
        presupuesto_restante = presupuesto_max or float('inf')
        
        destinos_seleccionados = []
        tiempo_usado = 0
        costo_usado = 0
        
        for item in destinos_con_score:
            destino = item['destino']
            
            # Estimar tiempo necesario para este destino
            num_actividades = item['num_actividades'] or 1
            tiempo_estimado = num_actividades * self.TIEMPO_PROMEDIO_ACTIVIDAD + self.TIEMPO_BUFFER
            
            # Verificar restricciones
            if tiempo_usado + tiempo_estimado <= minutos_disponibles:
                if costo_usado + float(destino.costo_entrada) <= presupuesto_restante:
                    destinos_seleccionados.append(item)
                    tiempo_usado += tiempo_estimado
                    costo_usado += float(destino.costo_entrada)
                    
                    # Limitar a máximo 2-3 destinos por día
                    if len(destinos_seleccionados) >= dias_totales * 2:
                        break
        
        return destinos_seleccionados
    
    def _seleccionar_actividades_por_destino(self, destinos_seleccionados, preferencias, presupuesto_max):
        """
        Selección de actividades ajustada a tus campos reales:
        - Filtra por 'disponible=True'
        - Usa 'tipo' para coincidencia de gustos
        """
        destinos_con_actividades = []
        
        # Normalizamos las preferencias del usuario a minúsculas para comparar bien
        preferencias_set = set([str(p).strip().lower() for p in preferencias])
        
        for item in destinos_seleccionados:
            destino = item['destino']
            
            # 1. Filtramos usando el campo correcto 'disponible'
            actividades = destino.actividades.filter(disponible=True)
            
            if not actividades.exists():
                destinos_con_actividades.append({
                    'destino': destino,
                    'actividades': [],
                    'score': item['score']
                })
                continue
            
            actividades_con_score = []
            
            for actividad in actividades:
                # 2. Usamos el campo 'tipo'
                # Convertimos el tipo de la actividad a minúscula y texto limpio
                tipo_actividad = str(actividad.tipo).strip().lower() if actividad.tipo else ""
                
                # Verificamos si el tipo está dentro de lo que le gusta al usuario
                # Ejemplo: si tipo es "museo" y usuario tiene ["museo", "playa"] -> Coincide
                match_val = 1.0 if tipo_actividad in preferencias_set else 0.0
                
                # Si no hay preferencias, damos un puntaje medio (0.5)
                score_actividad = match_val if preferencias else 0.5
                
                actividades_con_score.append({
                    'actividad': actividad,
                    'score': score_actividad
                })
            
            # Ordenamos por score y tomamos las 3 mejores
            actividades_con_score.sort(key=lambda x: x['score'], reverse=True)
            mejores_actividades = [a['actividad'] for a in actividades_con_score[:3]]
            
            destinos_con_actividades.append({
                'destino': destino,
                'actividades': mejores_actividades,
                'score': item['score']
            })
        
        return destinos_con_actividades
    
    def _ordenar_destinos_dijkstra(self, destinos_con_actividades):
        """
        ALGORITMO DE DIJKSTRA:
        Ordenar destinos para minimizar distancia total de viaje
        
        Simplificación: Como no tenemos coordenadas reales,
        usamos un orden basado en categorías y proximidad lógica
        
        En producción: usar coordenadas GPS y calcular distancias reales
        """
        
        # Si hay pocos destinos, no reordenar
        if len(destinos_con_actividades) <= 2:
            return destinos_con_actividades
        
        # Agrupar por categoría para simular proximidad
        por_categoria = defaultdict(list)
        for item in destinos_con_actividades:
            categoria = item['destino'].categoria.nombre if item['destino'].categoria else 'General'
            por_categoria[categoria].append(item)
        
        # Ordenar: primero una categoría, luego otra
        ordenados = []
        for categoria in sorted(por_categoria.keys()):
            ordenados.extend(por_categoria[categoria])
        
        return ordenados
    
    def _crear_itinerario(self, fecha_inicio, fecha_fin, destinos_ordenados, preferencias):
        """
        Crear el itinerario y distribuir destinos/actividades en días
        """
        
        dias_totales = (fecha_fin - fecha_inicio).days + 1
        
        # Crear itinerario
        itinerario = Itinerario.objects.create(
            turista=self.turista,
            nombre=f"Itinerario {fecha_inicio.strftime('%d/%m/%Y')}",
            descripcion=f"Generado automáticamente según tus preferencias: {', '.join(preferencias) if preferencias else 'sin preferencias específicas'}",
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
            estado='borrador'
        )
        
        # Distribuir destinos en días
        items_por_dia = self._distribuir_en_dias(destinos_ordenados, dias_totales)
        
        # Crear ItemItinerario para cada destino/actividad
        orden_global = 1
        costo_acumulado = Decimal('0.00')
        tiempo_acumulado = 0
        
        for dia, items in enumerate(items_por_dia, start=1):
            hora_actual = time(9, 0)  # Empezar a las 9 AM
            
            for item in items:
                destino = item['destino']
                actividades = item['actividades']
                
                # Calcular duración
                if actividades:
                    duracion_minutos = len(actividades) * self.TIEMPO_PROMEDIO_ACTIVIDAD
                else:
                    duracion_minutos = self.TIEMPO_PROMEDIO_ACTIVIDAD
                
                # Calcular hora_fin
                hora_fin_dt = datetime.combine(fecha_inicio, hora_actual) + timedelta(minutes=duracion_minutos)
                hora_fin = hora_fin_dt.time()
                
                # Crear notas con actividades
                notas = self._crear_notas_actividades(actividades)
                
                # Crear ItemItinerario
                ItemItinerario.objects.create(
                    itinerario=itinerario,
                    destino=destino,
                    orden=orden_global,
                    dia=dia,
                    hora_inicio=hora_actual,
                    hora_fin=hora_fin,
                    notas=notas
                )
                
                # Acumular costos y tiempos
                costo_acumulado += destino.costo_entrada
                tiempo_acumulado += duracion_minutos
                
                # Actualizar para siguiente item
                orden_global += 1
                hora_actual = (hora_fin_dt + timedelta(minutes=self.TIEMPO_BUFFER)).time()
        
        # Actualizar totales del itinerario
        itinerario.costo_total = costo_acumulado
        itinerario.tiempo_total_minutos = tiempo_acumulado
        itinerario.save()
        
        return itinerario
    
    def _distribuir_en_dias(self, destinos_ordenados, dias_totales):
        """
        Distribuir destinos equitativamente en los días disponibles
        """
        
        items_por_dia = [[] for _ in range(dias_totales)]
        
        # Distribuir round-robin
        for idx, item in enumerate(destinos_ordenados):
            dia_idx = idx % dias_totales
            items_por_dia[dia_idx].append(item)
        
        return items_por_dia
    
    def _crear_notas_actividades(self, actividades):
        """
        Crear string de notas con las actividades programadas
        """
        if not actividades:
            return "Visita libre al destino"
        
        notas_list = ["Actividades programadas:"]
        for act in actividades:
            notas_list.append(f"• {act.nombre} ({act.duracion_minutos} min)")
        
        return "\n".join(notas_list)
    
    def _crear_itinerario_vacio(self, fecha_inicio, fecha_fin):
        """
        Crear itinerario vacío cuando no hay destinos disponibles
        """
        return Itinerario.objects.create(
            turista=self.turista,
            nombre=f"Itinerario {fecha_inicio.strftime('%d/%m/%Y')}",
            descripcion="No se encontraron destinos que coincidan con tus preferencias. Intenta ajustar tus filtros.",
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
            estado='borrador'
        )


class AgregadorActividadesInteligente:
    """
    Permite agregar actividades dinámicamente a itinerarios existentes
    manteniendo la coherencia y optimización
    """
    
    def __init__(self, itinerario):
        self.itinerario = itinerario
    
    def agregar_actividad_auto(self, actividad, preferencias=None):
        """
        Agrega una actividad al itinerario en el mejor momento disponible
        """
        
        # Obtener items existentes
        items_existentes = self.itinerario.items.all().order_by('dia', 'orden')
        
        if not items_existentes.exists():
            # Si no hay items, crear el primero
            return self._crear_primer_item(actividad)
        
        # Encontrar mejor día para insertar
        mejor_dia = self._encontrar_mejor_dia(actividad, items_existentes, preferencias)
        
        # Insertar en el día seleccionado
        return self._insertar_en_dia(actividad, mejor_dia)
    
    def _encontrar_mejor_dia(self, actividad, items_existentes, preferencias):
        """
        Encuentra el día con más capacidad y mejor match de preferencias
        """
        
        # Calcular carga por día
        dias = {}
        for item in items_existentes:
            if item.dia not in dias:
                dias[item.dia] = {'tiempo': 0, 'items': []}
            
            duracion = (datetime.combine(datetime.today(), item.hora_fin) - 
                       datetime.combine(datetime.today(), item.hora_inicio)).seconds / 60
            dias[item.dia]['tiempo'] += duracion
            dias[item.dia]['items'].append(item)
        
        # Encontrar día con menos carga
        mejor_dia = min(dias.keys(), key=lambda d: dias[d]['tiempo'])
        
        return mejor_dia
    
    def _insertar_en_dia(self, actividad, dia):
        """
        Inserta la actividad en el día especificado
        """
        
        destino = actividad.destino
        items_dia = self.itinerario.items.filter(dia=dia).order_by('orden')
        
        if items_dia.exists():
            ultimo_item = items_dia.last()
            nuevo_orden = ultimo_item.orden + 1
            hora_inicio_dt = datetime.combine(datetime.today(), ultimo_item.hora_fin) + timedelta(minutes=30)
            hora_inicio = hora_inicio_dt.time()
        else:
            nuevo_orden = 1
            hora_inicio = time(9, 0)
        
        # Calcular hora fin
        hora_fin_dt = datetime.combine(datetime.today(), hora_inicio) + timedelta(minutes=actividad.duracion_minutos)
        hora_fin = hora_fin_dt.time()
        
        # Crear item
        item = ItemItinerario.objects.create(
            itinerario=self.itinerario,
            destino=destino,
            orden=nuevo_orden,
            dia=dia,
            hora_inicio=hora_inicio,
            hora_fin=hora_fin,
            notas=f"Actividad: {actividad.nombre}"
        )
        
        # Recalcular totales
        self.itinerario.calcular_totales()
        
        return item
    
    def _crear_primer_item(self, actividad):
        """
        Crea el primer item del itinerario
        """
        destino = actividad.destino
        
        item = ItemItinerario.objects.create(
            itinerario=self.itinerario,
            destino=destino,
            orden=1,
            dia=1,
            hora_inicio=time(9, 0),
            hora_fin=(datetime.combine(datetime.today(), time(9, 0)) + 
                     timedelta(minutes=actividad.duracion_minutos)).time(),
            notas=f"Actividad: {actividad.nombre}"
        )
        
        self.itinerario.calcular_totales()
        
        return item