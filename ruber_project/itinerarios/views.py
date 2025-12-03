from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import Itinerario, ItemItinerario
from .forms import GenerarItinerarioForm
from .generators import GeneradorItinerarios, RegeneradorActividades
from lugares.models import Actividad
from datetime import datetime, timedelta
import json

@login_required
def generar_itinerario(request):
    """
    Formulario para generar itinerario automático (SOLO UNA VEZ)
    """
    if request.method == 'POST':
        form = GenerarItinerarioForm(request.POST)
        if form.is_valid():
            datos = form.cleaned_data
            
            try:
                generador = GeneradorItinerarios(turista=request.user)
                itinerario = generador.generar(
                    fecha_inicio=datos['fecha_inicio'],
                    fecha_fin=datos['fecha_fin'],
                    preferencias=datos['preferencias'],
                    presupuesto_max=datos.get('presupuesto_max')
                )
                
                num_items = itinerario.items.count()
                
                if num_items > 0:
                    messages.success(
                        request, 
                        f'¡Itinerario generado con {num_items} actividades! '
                        f'Puedes regenerar actividades desde el dashboard.'
                    )
                else:
                    messages.warning(
                        request,
                        'No se encontraron destinos que coincidan. Intenta ajustar los filtros.'
                    )
                
                return redirect('itinerarios:detalle', itinerario_id=itinerario.id)
                
            except Exception as e:
                messages.error(request, f'Error: {str(e)}')
    else:
        form = GenerarItinerarioForm()
    
    context = {'form': form}
    return render(request, 'itinerarios/generar.html', context)


@login_required
def detalle_itinerario(request, itinerario_id):
    """
    Dashboard del itinerario con métricas REALES
    CORREGIDO: Ahora extrae costos de las actividades reales
    """
    itinerario = get_object_or_404(Itinerario, id=itinerario_id, turista=request.user)
    
    # Recalcular totales para asegurar datos actualizados
    itinerario.calcular_totales()
    itinerario.refresh_from_db()
    
    items = itinerario.items.all().select_related('destino', 'destino__categoria')
    
    # Agrupar items por día
    items_por_dia = {}
    for item in items:
        if item.dia not in items_por_dia:
            items_por_dia[item.dia] = []
        items_por_dia[item.dia].append(item)
    
    # Calcular estadísticas
    total_destinos = items.values('destino').distinct().count()
    total_dias = len(items_por_dia) if items_por_dia else 1
    promedio_actividades_dia = items.count() / total_dias if total_dias > 0 else 0
    
    # Datos para gráficos - CORREGIDO
    datos_grafico = {
        'dias': [],
        'actividades': [],
        'tiempo': [],
        'costo': []
    }
    
    if items.exists():
        for dia in sorted(items_por_dia.keys()):
            items_dia = items_por_dia[dia]
            
            # Calcular tiempo REAL del día
            tiempo_dia = 0
            for item in items_dia:
                if item.hora_inicio and item.hora_fin:
                    inicio_dt = datetime.combine(datetime.today(), item.hora_inicio)
                    fin_dt = datetime.combine(datetime.today(), item.hora_fin)
                    
                    # Manejar casos donde hora_fin es menor (cruza medianoche)
                    if fin_dt < inicio_dt:
                        fin_dt += timedelta(days=1)
                    
                    tiempo_dia += (fin_dt - inicio_dt).seconds / 60
            
            # Calcular costo REAL del día (extrayendo de notas)
            costo_dia = 0
            for item in items_dia:
                # Intentar extraer costo de las notas
                costo_item = None
                
                if item.notas and 'Costo:' in item.notas:
                    try:
                        import re
                        match = re.search(r'S/\s*(\d+\.?\d*)', item.notas)
                        if match:
                            costo_item = float(match.group(1))
                    except:
                        pass
                
                # Fallback al costo del destino
                if costo_item is None:
                    costo_item = float(item.destino.costo_entrada)
                
                costo_dia += costo_item
            
            datos_grafico['dias'].append(f'Día {dia}')
            datos_grafico['actividades'].append(len(items_dia))
            datos_grafico['tiempo'].append(int(tiempo_dia))
            datos_grafico['costo'].append(round(costo_dia, 2))
    else:
        # Datos vacíos si no hay items
        datos_grafico = {
            'dias': ['Sin datos'],
            'actividades': [0],
            'tiempo': [0],
            'costo': [0]
        }
    
    context = {
        'itinerario': itinerario,
        'items': items,
        'items_por_dia': items_por_dia,
        'total_destinos': total_destinos,
        'total_dias': total_dias,
        'promedio_actividades_dia': round(promedio_actividades_dia, 1),
        'datos_grafico': json.dumps(datos_grafico),
    }
    return render(request, 'itinerarios/detalle_itinerario.html', context)


@login_required
def regenerar_actividades(request, itinerario_id):
    """
    Regenera 3 actividades aleatorias para el itinerario
    """
    itinerario = get_object_or_404(Itinerario, id=itinerario_id, turista=request.user)
    
    try:
        # Obtener preferencias del usuario si existen
        preferencias = []
        if hasattr(request.user, 'preferencias') and request.user.preferencias:
            preferencias = request.user.preferencias.split(',')
        
        # Regenerar actividades
        regenerador = RegeneradorActividades(itinerario)
        regenerador.regenerar_3_actividades(preferencias)
        
        messages.success(request, '¡3 nuevas actividades generadas exitosamente!')
        
    except Exception as e:
        messages.error(request, f'Error al regenerar actividades: {str(e)}')
    
    return redirect('itinerarios:detalle', itinerario_id=itinerario.id)


@login_required
def mis_itinerarios(request):
    """
    Lista de itinerarios (NO borra nada, solo muestra)
    """
    itinerarios = Itinerario.objects.filter(turista=request.user).order_by('-fecha_creacion')
    
    # Agregar estadísticas calculadas
    for itinerario in itinerarios:
        itinerario.num_actividades = itinerario.items.count()
        itinerario.num_destinos = itinerario.items.values('destino').distinct().count()
        itinerario.num_dias = itinerario.items.values('dia').distinct().count() or 1
    
    context = {
        'itinerarios': itinerarios,
        'total_itinerarios': itinerarios.count(),
    }
    
    return render(request, 'itinerarios/mis_itinerarios.html', context)


@login_required
def eliminar_item(request, item_id):
    """
    Eliminar un item del itinerario
    """
    item = get_object_or_404(ItemItinerario, id=item_id, itinerario__turista=request.user)
    itinerario = item.itinerario
    
    item.delete()
    itinerario.calcular_totales()
    
    messages.success(request, 'Actividad eliminada del itinerario')
    return redirect('itinerarios:detalle', itinerario_id=itinerario.id)


@login_required
def eliminar_itinerario(request, itinerario_id):
    """
    Eliminar un itinerario completo
    """
    itinerario = get_object_or_404(Itinerario, id=itinerario_id, turista=request.user)
    
    nombre = itinerario.nombre
    itinerario.delete()
    
    messages.success(request, f'Itinerario "{nombre}" eliminado exitosamente')
    return redirect('itinerarios:mis_itinerarios')


@login_required
def duplicar_itinerario(request, itinerario_id):
    """
    Duplicar un itinerario existente
    """
    itinerario_original = get_object_or_404(Itinerario, id=itinerario_id, turista=request.user)
    
    # Crear copia
    itinerario_nuevo = Itinerario.objects.create(
        turista=request.user,
        nombre=f"{itinerario_original.nombre} (Copia)",
        descripcion=itinerario_original.descripcion,
        fecha_inicio=itinerario_original.fecha_inicio,
        fecha_fin=itinerario_original.fecha_fin,
        estado='borrador'
    )
    
    # Copiar items
    for item_original in itinerario_original.items.all():
        ItemItinerario.objects.create(
            itinerario=itinerario_nuevo,
            destino=item_original.destino,
            orden=item_original.orden,
            dia=item_original.dia,
            hora_inicio=item_original.hora_inicio,
            hora_fin=item_original.hora_fin,
            notas=item_original.notas
        )
    
    # Calcular totales
    itinerario_nuevo.calcular_totales()
    
    messages.success(request, 'Itinerario duplicado exitosamente')
    return redirect('itinerarios:detalle', itinerario_id=itinerario_nuevo.id)