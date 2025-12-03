from datetime import timedelta, time, datetime
from decimal import Decimal
from lugares.models import Destino, Actividad
from .models import Itinerario, ItemItinerario
from django.db.models import Q
import random

class GeneradorItinerarios:
    """
    Generador de itinerarios usando Matemática Discreta
    CORREGIDO: Ahora selecciona actividades reales con sus costos y duraciones
    """
    
    # Constantes para ponderación
    PESO_CALIFICACION = 0.4
    PESO_PREFERENCIA = 0.35
    PESO_COSTO = 0.15
    PESO_POPULARIDAD = 0.1
    
    # Valores por defecto cuando NO hay actividad
    TIEMPO_DEFAULT = 90  # minutos
    COSTO_DEFAULT = Decimal('20.00')  # soles
    TIEMPO_BUFFER = 30  # minutos entre actividades
    MAX_ACTIVIDADES_TOTAL = 3  # MÁXIMO 3 ACTIVIDADES
    
    def __init__(self, turista):
        self.turista = turista
        
    def generar(self, fecha_inicio, fecha_fin, preferencias, presupuesto_max=None):
        """
        Genera un itinerario óptimo con actividades reales y métricas correctas
        """
        
        # Asegurar que preferencias sea una lista
        if isinstance(preferencias, str):
            preferencias = [p.strip() for p in preferencias.split(',') if p.strip()]
        elif not isinstance(preferencias, list):
            preferencias = list(preferencias) if preferencias else []
        
        # 1. Filtrar destinos por preferencias
        destinos_candidatos = self._filtrar_destinos_por_preferencias(
            preferencias, 
            presupuesto_max
        )
        
        if not destinos_candidatos:
            return self._crear_itinerario_vacio(fecha_inicio, fecha_fin)
        
        # 2. Calcular scoring
        destinos_con_score = self._calcular_scores(
            destinos_candidatos, 
            preferencias, 
            presupuesto_max
        )
        
        # 3. Seleccionar top 3 destinos
        destinos_seleccionados = self._seleccionar_top_3_destinos(
            destinos_con_score,
            presupuesto_max
        )
        
        # 4. CREAR ITINERARIO CON ACTIVIDADES REALES
        itinerario = self._crear_itinerario_con_actividades_reales(
            fecha_inicio, 
            fecha_fin, 
            destinos_seleccionados,
            preferencias,
            presupuesto_max
        )
        
        return itinerario
    
    def _filtrar_destinos_por_preferencias(self, preferencias, presupuesto_max):
        """
        Filtrar destinos por intersección de preferencias
        """
        destinos = Destino.objects.filter(activo=True)
        
        if presupuesto_max:
            destinos = destinos.filter(costo_entrada__lte=presupuesto_max)
        
        if preferencias:
            filtro_tags = Q()
            for pref in preferencias:
                filtro_tags |= Q(tags_preferencias__icontains=pref)
            
            destinos = destinos.filter(filtro_tags).distinct()
        
        return list(destinos.prefetch_related('actividades'))
    
    def _calcular_scores(self, destinos, preferencias, presupuesto_max):
        """
        Calcular scoring de cada destino
        """
        destinos_con_score = []
        max_actividades = max([d.actividades.count() for d in destinos]) if destinos else 1
        
        for destino in destinos:
            # Componente 1: Calificación
            calificacion_valor = float(destino.calificacion) if destino.calificacion else 3.0
            score_calificacion = calificacion_valor / 5.0
            
            # Componente 2: Match de preferencias
            raw_tags = destino.tags_preferencias or []
            
            if isinstance(raw_tags, str):
                lista_tags = raw_tags.split(',')
            elif isinstance(raw_tags, list):
                lista_tags = raw_tags
            else:
                lista_tags = []

            tags_destino = set([str(tag).strip().lower() for tag in lista_tags])
            preferencias_set = set([p.lower() for p in preferencias])
            interseccion = tags_destino & preferencias_set
            
            score_preferencias = len(interseccion) / float(len(preferencias)) if preferencias else 0.5
            
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

    def _seleccionar_top_3_destinos(self, destinos_con_score, presupuesto_max):
        """
        Selecciona MÁXIMO 3 destinos
        """
        presupuesto_restante = float(presupuesto_max) if presupuesto_max else float('inf')
        
        destinos_seleccionados = []
        costo_usado = 0
        
        for item in destinos_con_score:
            if len(destinos_seleccionados) >= self.MAX_ACTIVIDADES_TOTAL:
                break
                
            destino = item['destino']
            costo_destino = float(destino.costo_entrada)
            
            if costo_usado + costo_destino <= presupuesto_restante:
                destinos_seleccionados.append(item)
                costo_usado += costo_destino
        
        return destinos_seleccionados
    
    def _crear_itinerario_con_actividades_reales(self, fecha_inicio, fecha_fin, destinos_seleccionados, preferencias, presupuesto_max):
        """
        MÉTODO PRINCIPAL CORREGIDO:
        Crea itinerario seleccionando ACTIVIDADES REALES con sus costos y duraciones
        """
        
        # Crear itinerario
        itinerario = Itinerario.objects.create(
            turista=self.turista,
            nombre=f"Itinerario {fecha_inicio.strftime('%d/%m/%Y')}",
            descripcion=f"Generado automáticamente según tus preferencias: {', '.join(preferencias) if preferencias else 'sin preferencias específicas'}",
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
            estado='borrador'
        )
        
        # Variables para tracking
        orden_global = 1
        costo_total_acumulado = Decimal('0.00')
        tiempo_total_acumulado = 0
        
        hora_actual = time(9, 0)  # Empezar a las 9 AM
        dia = 1
        
        for item in destinos_seleccionados:
            destino = item['destino']
            
            # ========================================
            # PASO CRÍTICO: SELECCIONAR ACTIVIDAD REAL
            # ========================================
            actividad_seleccionada = self._seleccionar_actividad_real(destino, preferencias)
            
            # Determinar costo y duración
            if actividad_seleccionada:
                # USAR DATOS REALES DE LA ACTIVIDAD
                costo_actividad = actividad_seleccionada.costo if hasattr(actividad_seleccionada, 'costo') and actividad_seleccionada.costo else destino.costo_entrada
                duracion_minutos = actividad_seleccionada.duracion_minutos if actividad_seleccionada.duracion_minutos else self.TIEMPO_DEFAULT
                
                # Notas con información de la actividad
                notas = f"🎯 Actividad: {actividad_seleccionada.nombre}\n"
                notas += f"⏱️ Duración: {duracion_minutos} minutos\n"
                notas += f"💰 Costo: S/ {costo_actividad}\n"
                if actividad_seleccionada.descripcion:
                    notas += f"📝 {actividad_seleccionada.descripcion[:100]}"
            else:
                # FALLBACK: Usar valores por defecto
                costo_actividad = destino.costo_entrada if destino.costo_entrada else self.COSTO_DEFAULT
                duracion_minutos = self.TIEMPO_DEFAULT
                
                notas = f"🏛️ Visita libre a {destino.nombre}\n"
                notas += f"⏱️ Duración estimada: {duracion_minutos} minutos\n"
                notas += f"💰 Costo de entrada: S/ {costo_actividad}"
            
            # Calcular hora_fin
            hora_fin_dt = datetime.combine(fecha_inicio, hora_actual) + timedelta(minutes=duracion_minutos)
            hora_fin = hora_fin_dt.time()
            
            # CREAR ITEM ITINERARIO CON DATOS REALES
            ItemItinerario.objects.create(
                itinerario=itinerario,
                destino=destino,
                orden=orden_global,
                dia=dia,
                hora_inicio=hora_actual,
                hora_fin=hora_fin,
                notas=notas
            )
            
            # Acumular métricas REALES
            costo_total_acumulado += Decimal(str(costo_actividad))
            tiempo_total_acumulado += int(duracion_minutos)
            
            # Siguiente item
            orden_global += 1
            hora_actual = (hora_fin_dt + timedelta(minutes=self.TIEMPO_BUFFER)).time()
        
        # Guardar totales en el itinerario
        itinerario.costo_total = costo_total_acumulado
        itinerario.tiempo_total_minutos = tiempo_total_acumulado
        itinerario.save()
        
        # Llamar al método de recálculo para asegurar consistencia
        itinerario.calcular_totales()
        
        return itinerario
    
    def _seleccionar_actividad_real(self, destino, preferencias):
        """
        MÉTODO CLAVE: Selecciona UNA actividad real del destino
        
        Lógica:
        1. Busca actividades disponibles
        2. Si hay preferencias, intenta encontrar coincidencia
        3. Si no, selecciona una aleatoria
        4. Si no hay actividades, retorna None (usar fallback)
        """
        # Buscar actividades disponibles
        actividades = destino.actividades.filter(disponible=True)
        
        if not actividades.exists():
            return None  # No hay actividades, usar fallback
        
        # Si hay preferencias, buscar mejor match
        if preferencias:
            preferencias_set = set([str(p).strip().lower() for p in preferencias])
            
            actividades_con_score = []
            
            for actividad in actividades:
                # Calcular coincidencia con preferencias
                tipo_actividad = str(actividad.tipo).strip().lower() if actividad.tipo else ""
                
                # Score: 1.0 si coincide con alguna preferencia, 0.0 si no
                score = 1.0 if tipo_actividad in preferencias_set else 0.0
                
                actividades_con_score.append({
                    'actividad': actividad,
                    'score': score
                })
            
            # Ordenar por score
            actividades_con_score.sort(key=lambda x: x['score'], reverse=True)
            
            # Retornar la mejor (o una aleatoria entre las top 3)
            top_actividades = [a['actividad'] for a in actividades_con_score[:3]]
            return random.choice(top_actividades)
        
        # Si no hay preferencias, seleccionar aleatoria
        return random.choice(list(actividades))
    
    def _crear_itinerario_vacio(self, fecha_inicio, fecha_fin):
        """
        Crear itinerario vacío cuando no hay destinos
        """
        return Itinerario.objects.create(
            turista=self.turista,
            nombre=f"Itinerario {fecha_inicio.strftime('%d/%m/%Y')}",
            descripcion="No se encontraron destinos que coincidan con tus preferencias. Intenta ajustar tus filtros.",
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
            estado='borrador'
        )


class RegeneradorActividades:
    """
    Regenera 3 actividades aleatorias con sus costos y duraciones reales
    """
    
    TIEMPO_DEFAULT = 90
    COSTO_DEFAULT = Decimal('20.00')
    TIEMPO_BUFFER = 30
    
    def __init__(self, itinerario):
        self.itinerario = itinerario
    
    def regenerar_3_actividades(self, preferencias=None):
        """
        Elimina actividades actuales y genera 3 nuevas con datos reales
        """
        # 1. Eliminar actividades actuales
        self.itinerario.items.all().delete()
        
        # 2. Obtener destinos disponibles
        destinos = Destino.objects.filter(activo=True)
        
        # Filtrar por preferencias
        if preferencias:
            if isinstance(preferencias, str):
                preferencias = [p.strip() for p in preferencias.split(',') if p.strip()]
            
            filtro_tags = Q()
            for pref in preferencias:
                filtro_tags |= Q(tags_preferencias__icontains=pref)
            
            destinos = destinos.filter(filtro_tags).distinct()
        
        destinos_lista = list(destinos)
        
        if len(destinos_lista) < 3:
            destinos_seleccionados = destinos_lista
        else:
            destinos_seleccionados = random.sample(destinos_lista, 3)
        
        # 3. Crear items con actividades reales
        orden = 1
        hora_actual = time(9, 0)
        costo_total = Decimal('0.00')
        tiempo_total = 0
        
        for destino in destinos_seleccionados:
            # SELECCIONAR ACTIVIDAD REAL
            actividades = destino.actividades.filter(disponible=True)
            actividad = random.choice(list(actividades)) if actividades.exists() else None
            
            # Usar datos reales o fallback
            if actividad:
                costo = actividad.costo if hasattr(actividad, 'costo') and actividad.costo else destino.costo_entrada
                duracion = actividad.duracion_minutos if actividad.duracion_minutos else self.TIEMPO_DEFAULT
                
                notas = f"🎯 Actividad: {actividad.nombre}\n"
                notas += f"⏱️ Duración: {duracion} minutos\n"
                notas += f"💰 Costo: S/ {costo}"
            else:
                costo = destino.costo_entrada if destino.costo_entrada else self.COSTO_DEFAULT
                duracion = self.TIEMPO_DEFAULT
                
                notas = f"🏛️ Visita libre a {destino.nombre}\n"
                notas += f"⏱️ Duración: {duracion} minutos\n"
                notas += f"💰 Costo: S/ {costo}"
            
            # Calcular hora fin
            hora_fin_dt = datetime.combine(datetime.today(), hora_actual) + timedelta(minutes=duracion)
            hora_fin = hora_fin_dt.time()
            
            # Crear item
            ItemItinerario.objects.create(
                itinerario=self.itinerario,
                destino=destino,
                orden=orden,
                dia=1,
                hora_inicio=hora_actual,
                hora_fin=hora_fin,
                notas=notas
            )
            
            costo_total += Decimal(str(costo))
            tiempo_total += int(duracion)
            
            orden += 1
            hora_actual = (hora_fin_dt + timedelta(minutes=self.TIEMPO_BUFFER)).time()
        
        # 4. Actualizar totales
        self.itinerario.costo_total = costo_total
        self.itinerario.tiempo_total_minutos = tiempo_total
        self.itinerario.save()
        self.itinerario.calcular_totales()
        
        return self.itinerario