from datetime import timedelta, time, datetime
from decimal import Decimal
from lugares.models import Destino, Actividad
from .models import Itinerario, ItemItinerario
from django.db.models import Q
import random

class GeneradorItinerarios:
    """
    Generador de itinerarios con control ESTRICTO de presupuesto
    """
    
    # Constantes para ponderación
    PESO_CALIFICACION = 0.4
    PESO_PREFERENCIA = 0.35
    PESO_COSTO = 0.15
    PESO_POPULARIDAD = 0.1
    
    # Valores por defecto
    TIEMPO_DEFAULT = 90
    COSTO_DEFAULT = Decimal('20.00')
    TIEMPO_BUFFER = 30
    MAX_ACTIVIDADES_TOTAL = 3
    
    def __init__(self, turista):
        self.turista = turista
        
    def generar(self, nombre_itinerario, fecha_inicio, fecha_fin):
        """
        Genera un itinerario usando las preferencias y presupuesto del usuario
        
        Args:
            nombre_itinerario: Nombre personalizado del itinerario
            fecha_inicio: Fecha de inicio
            fecha_fin: Fecha de fin
        """
        # Obtener preferencias y presupuesto del perfil del usuario
        preferencias = self.turista.preferencias if self.turista.preferencias else []
        presupuesto_max = self.turista.presupuesto_max
        
        # Asegurar que preferencias sea una lista
        if isinstance(preferencias, str):
            preferencias = [p.strip() for p in preferencias.split(',') if p.strip()]
        elif not isinstance(preferencias, list):
            preferencias = list(preferencias) if preferencias else []
        
        print(f" Generando itinerario para {self.turista.username}")
        print(f"   Preferencias: {preferencias}")
        print(f"   Presupuesto máximo: {presupuesto_max}")
        
        # 1. Filtrar destinos
        destinos_candidatos = self._filtrar_destinos_por_preferencias(
            preferencias, 
            presupuesto_max
        )
        
        if not destinos_candidatos:
            return self._crear_itinerario_vacio(nombre_itinerario, fecha_inicio, fecha_fin)
        
        # 2. Calcular scoring
        destinos_con_score = self._calcular_scores(
            destinos_candidatos, 
            preferencias, 
            presupuesto_max
        )
        
        # 3. Seleccionar top destinos RESPETANDO PRESUPUESTO
        destinos_seleccionados = self._seleccionar_destinos_con_presupuesto(
            destinos_con_score,
            presupuesto_max
        )
        
        # 4. Crear itinerario con actividades reales
        itinerario = self._crear_itinerario_con_actividades_reales(
            nombre_itinerario,
            fecha_inicio, 
            fecha_fin, 
            destinos_seleccionados,
            preferencias,
            presupuesto_max
        )
        
        return itinerario
    
    def _filtrar_destinos_por_preferencias(self, preferencias, presupuesto_max):
        """Filtrar destinos por preferencias y presupuesto"""
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
        """Calcular scoring de cada destino"""
        destinos_con_score = []
        max_actividades = max([d.actividades.count() for d in destinos]) if destinos else 1
        
        for destino in destinos:
            calificacion_valor = float(destino.calificacion) if destino.calificacion else 3.0
            score_calificacion = calificacion_valor / 5.0
            
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
            
            if presupuesto_max and float(presupuesto_max) > 0:
                costo_destino = float(destino.costo_entrada) if destino.costo_entrada else 0.0
                score_costo = 1 - (costo_destino / float(presupuesto_max))
                score_costo = max(0.0, min(1.0, score_costo))
            else:
                score_costo = 0.5
            
            num_actividades = destino.actividades.count()
            score_popularidad = num_actividades / float(max_actividades) if max_actividades > 0 else 0.5
            
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

    def _seleccionar_destinos_con_presupuesto(self, destinos_con_score, presupuesto_max):
        """
        CRÍTICO: Selecciona destinos sin superar el presupuesto
        """
        if not presupuesto_max:
            # Sin límite de presupuesto, tomar top 3
            return destinos_con_score[:self.MAX_ACTIVIDADES_TOTAL]
        
        presupuesto_restante = float(presupuesto_max)
        destinos_seleccionados = []
        costo_acumulado = 0.0
        
        print(f"💰 Presupuesto disponible: S/ {presupuesto_restante}")
        
        for item in destinos_con_score:
            if len(destinos_seleccionados) >= self.MAX_ACTIVIDADES_TOTAL:
                break
            
            destino = item['destino']
            
            # Buscar actividad más barata disponible
            actividades = destino.actividades.filter(disponible=True).order_by('costo')
            
            if actividades.exists():
                actividad_mas_barata = actividades.first()
                costo_item = float(actividad_mas_barata.costo)
            else:
                costo_item = float(destino.costo_entrada) if destino.costo_entrada else float(self.COSTO_DEFAULT)
            
            # Verificar si cabe en el presupuesto
            if costo_acumulado + costo_item <= presupuesto_restante:
                destinos_seleccionados.append(item)
                costo_acumulado += costo_item
                print(f"   ✅ {destino.nombre}: S/ {costo_item} (Total: S/ {costo_acumulado})")
            else:
                print(f"   ❌ {destino.nombre}: S/ {costo_item} (Excede presupuesto)")
        
        print(f"📊 Total seleccionado: {len(destinos_seleccionados)} destinos por S/ {costo_acumulado}")
        
        return destinos_seleccionados
    
    def _crear_itinerario_con_actividades_reales(self, nombre, fecha_inicio, fecha_fin, 
                                                   destinos_seleccionados, preferencias, presupuesto_max):
        """Crea itinerario con actividades reales"""
        
        itinerario = Itinerario.objects.create(
            turista=self.turista,
            nombre=nombre,  # Usar el nombre personalizado
            descripcion=f"Generado según tus preferencias: {', '.join(preferencias) if preferencias else 'sin preferencias específicas'}",
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
            estado='borrador'
        )
        
        orden_global = 1
        costo_total_acumulado = Decimal('0.00')
        tiempo_total_acumulado = 0
        
        hora_actual = time(9, 0)
        dia = 1
        
        for item in destinos_seleccionados:
            destino = item['destino']
            
            actividad_seleccionada = self._seleccionar_actividad_real(destino, preferencias)
            
            if actividad_seleccionada:
                costo_actividad = actividad_seleccionada.costo if hasattr(actividad_seleccionada, 'costo') and actividad_seleccionada.costo else destino.costo_entrada
                duracion_minutos = actividad_seleccionada.duracion_minutos if actividad_seleccionada.duracion_minutos else self.TIEMPO_DEFAULT
                
                notas = f" Actividad: {actividad_seleccionada.nombre}\n"
                notas += f" Duración: {duracion_minutos} minutos\n"
                notas += f" Costo: S/ {costo_actividad}\n"
                if actividad_seleccionada.descripcion:
                    notas += f" {actividad_seleccionada.descripcion[:100]}"
            else:
                costo_actividad = destino.costo_entrada if destino.costo_entrada else self.COSTO_DEFAULT
                duracion_minutos = self.TIEMPO_DEFAULT
                
                notas = f" Visita libre a {destino.nombre}\n"
                notas += f" Duración estimada: {duracion_minutos} minutos\n"
                notas += f" Costo de entrada: S/ {costo_actividad}"
            
            hora_fin_dt = datetime.combine(fecha_inicio, hora_actual) + timedelta(minutes=duracion_minutos)
            hora_fin = hora_fin_dt.time()
            
            ItemItinerario.objects.create(
                itinerario=itinerario,
                destino=destino,
                orden=orden_global,
                dia=dia,
                hora_inicio=hora_actual,
                hora_fin=hora_fin,
                notas=notas
            )
            
            costo_total_acumulado += Decimal(str(costo_actividad))
            tiempo_total_acumulado += int(duracion_minutos)
            
            orden_global += 1
            hora_actual = (hora_fin_dt + timedelta(minutes=self.TIEMPO_BUFFER)).time()
        
        itinerario.costo_total = costo_total_acumulado
        itinerario.tiempo_total_minutos = tiempo_total_acumulado
        itinerario.save()
        itinerario.calcular_totales()
        
        return itinerario
    
    def _seleccionar_actividad_real(self, destino, preferencias):
        """Selecciona una actividad real del destino"""
        actividades = destino.actividades.filter(disponible=True)
        
        if not actividades.exists():
            return None
        
        if preferencias:
            preferencias_set = set([str(p).strip().lower() for p in preferencias])
            
            actividades_con_score = []
            for actividad in actividades:
                tipo_actividad = str(actividad.tipo).strip().lower() if actividad.tipo else ""
                score = 1.0 if tipo_actividad in preferencias_set else 0.0
                actividades_con_score.append({'actividad': actividad, 'score': score})
            
            actividades_con_score.sort(key=lambda x: x['score'], reverse=True)
            top_actividades = [a['actividad'] for a in actividades_con_score[:3]]
            return random.choice(top_actividades)
        
        return random.choice(list(actividades))
    
    def _crear_itinerario_vacio(self, nombre, fecha_inicio, fecha_fin):
        """Crear itinerario vacío cuando no hay destinos"""
        return Itinerario.objects.create(
            turista=self.turista,
            nombre=nombre,
            descripcion="No se encontraron destinos que coincidan con tus preferencias y presupuesto. Intenta ajustar tu perfil.",
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
            estado='borrador'
        )


class RegeneradorActividades:
    """Regenera actividades respetando presupuesto"""
    
    TIEMPO_DEFAULT = 90
    COSTO_DEFAULT = Decimal('20.00')
    TIEMPO_BUFFER = 30
    
    def __init__(self, itinerario):
        self.itinerario = itinerario
    
    def regenerar_3_actividades(self):
        """Regenera 3 actividades respetando el presupuesto del usuario"""
        
        # Eliminar actividades actuales
        self.itinerario.items.all().delete()
        
        # Obtener presupuesto del usuario
        presupuesto_max = self.itinerario.turista.presupuesto_max
        preferencias = self.itinerario.turista.preferencias if self.itinerario.turista.preferencias else []
        
        if isinstance(preferencias, str):
            preferencias = [p.strip() for p in preferencias.split(',') if p.strip()]
        
        # Obtener destinos
        destinos = Destino.objects.filter(activo=True)
        
        if preferencias:
            filtro_tags = Q()
            for pref in preferencias:
                filtro_tags |= Q(tags_preferencias__icontains=pref)
            destinos = destinos.filter(filtro_tags).distinct()
        
        destinos_lista = list(destinos)
        
        if not destinos_lista:
            return self.itinerario
        
        # Seleccionar 3 destinos con presupuesto
        destinos_seleccionados = []
        costo_acumulado = Decimal('0.00')
        presupuesto_decimal = Decimal(str(presupuesto_max)) if presupuesto_max else None
        
        random.shuffle(destinos_lista)
        
        for destino in destinos_lista:
            if len(destinos_seleccionados) >= 3:
                break
            
            # Buscar actividad más barata
            actividades = destino.actividades.filter(disponible=True).order_by('costo')
            
            if actividades.exists():
                actividad = actividades.first()
                costo = actividad.costo if hasattr(actividad, 'costo') and actividad.costo else destino.costo_entrada
            else:
                costo = destino.costo_entrada if destino.costo_entrada else self.COSTO_DEFAULT
            
            # Verificar presupuesto
            if presupuesto_decimal:
                if costo_acumulado + Decimal(str(costo)) <= presupuesto_decimal:
                    destinos_seleccionados.append(destino)
                    costo_acumulado += Decimal(str(costo))
            else:
                destinos_seleccionados.append(destino)
                costo_acumulado += Decimal(str(costo))
        
        # Crear items
        orden = 1
        hora_actual = time(9, 0)
        tiempo_total = 0
        
        for destino in destinos_seleccionados:
            actividades = destino.actividades.filter(disponible=True)
            actividad = random.choice(list(actividades)) if actividades.exists() else None
            
            if actividad:
                costo = actividad.costo if hasattr(actividad, 'costo') and actividad.costo else destino.costo_entrada
                duracion = actividad.duracion_minutos if actividad.duracion_minutos else self.TIEMPO_DEFAULT
                
                notas = f" Actividad: {actividad.nombre}\n"
                notas += f" Duración: {duracion} minutos\n"
                notas += f" Costo: S/ {costo}"
            else:
                costo = destino.costo_entrada if destino.costo_entrada else self.COSTO_DEFAULT
                duracion = self.TIEMPO_DEFAULT
                
                notas = f" Visita libre a {destino.nombre}\n"
                notas += f" Duración: {duracion} minutos\n"
                notas += f" Costo: S/ {costo}"
            
            hora_fin_dt = datetime.combine(datetime.today(), hora_actual) + timedelta(minutes=duracion)
            hora_fin = hora_fin_dt.time()
            
            ItemItinerario.objects.create(
                itinerario=self.itinerario,
                destino=destino,
                orden=orden,
                dia=1,
                hora_inicio=hora_actual,
                hora_fin=hora_fin,
                notas=notas
            )
            
            tiempo_total += int(duracion)
            orden += 1
            hora_actual = (hora_fin_dt + timedelta(minutes=self.TIEMPO_BUFFER)).time()
        
        # Actualizar totales
        self.itinerario.costo_total = costo_acumulado
        self.itinerario.tiempo_total_minutos = tiempo_total
        self.itinerario.save()
        self.itinerario.calcular_totales()
        
        return self.itinerario