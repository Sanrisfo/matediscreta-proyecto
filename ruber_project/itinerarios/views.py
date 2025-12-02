from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import Itinerario, ItemItinerario
from .forms import GenerarItinerarioForm
from .generators import GeneradorItinerarios, AgregadorActividadesInteligente
from lugares.models import Actividad
from datetime import datetime
import json

@login_required
def generar_itinerario(request):
    """
    Formulario para generar itinerario automático usando algoritmos
    de Matemática Discreta
    """
    if request.method == 'POST':
        form = GenerarItinerarioForm(request.POST)
        if form.is_valid():
            # Extraer datos del formulario
            datos = form.cleaned_data
            
            try:
                # Generar itinerario usando el algoritmo inteligente
                generador = GeneradorItinerarios(turista=request.user)
                itinerario = generador.generar(
                    fecha_inicio=datos['fecha_inicio'],
                    fecha_fin=datos['fecha_fin'],
                    preferencias=datos['preferencias'],
                    presupuesto_max=datos.get('presupuesto_max')
                )
                
                # Verificar si se generaron items
                if itinerario.items.count() > 0:
                    messages.success(
                        request, 
                        f'¡Itinerario generado exitosamente! '
                        f'Se han seleccionado {itinerario.items.count()} actividades '
                        f'en {itinerario.items.values("dia").distinct().count()} días.'
                    )
                else:
                    messages.warning(
                        request,
                        'No se encontraron destinos que coincidan con tus preferencias. '
                        'Intenta ajustar los filtros o ampliar el presupuesto.'
                    )
                
                return redirect('itinerarios:detalle', itinerario_id=itinerario.id)
                
            except Exception as e:
                messages.error(
                    request,
                    f'Error al generar el itinerario: {str(e)}. Por favor intenta nuevamente.'
                )
    else:
        form = GenerarItinerarioForm()
    
    # Obtener estadísticas para mostrar en la página
    total_destinos = request.user.destinos.filter(activo=True).count() if hasattr(request.user, 'destinos') else 0
    
    context = {
        'form': form,
        'total_destinos': total_destinos,
    }
    
    return render(request, 'itinerarios/generar.html', context)


@login_required
def detalle_itinerario(request, itinerario_id):
    """
    Ver detalle de un itinerario con visualización de cronograma
    """
    itinerario = get_object_or_404(Itinerario, id=itinerario_id, turista=request.user)
    items = itinerario.items.all().select_related('destino', 'destino__categoria')
    
    # Agrupar items por día para el cronograma
    items_por_dia = {}
    for item in items:
        if item.dia not in items_por_dia:
            items_por_dia[item.dia] = []
        items_por_dia[item.dia].append(item)
    
    # Calcular estadísticas
    total_destinos = items.values('destino').distinct().count()
    total_dias = len(items_por_dia)
    promedio_actividades_dia = items.count() / total_dias if total_dias > 0 else 0
    
    # Datos para gráfico (JSON)
    datos_grafico = {
        'dias': [],
        'actividades': [],
        'tiempo': [],
        'costo': []
    }
    
    for dia in sorted(items_por_dia.keys()):
        items_dia = items_por_dia[dia]
        tiempo_dia = sum([
            (datetime.combine(datetime.today(), item.hora_fin) - 
             datetime.combine(datetime.today(), item.hora_inicio)).seconds / 60
            for item in items_dia
        ])
        costo_dia = sum([float(item.destino.costo_entrada) for item in items_dia])
        
        datos_grafico['dias'].append(f'Día {dia}')
        datos_grafico['actividades'].append(len(items_dia))
        datos_grafico['tiempo'].append(int(tiempo_dia))
        datos_grafico['costo'].append(costo_dia)
    
    context = {
        'itinerario': itinerario,
        'items': items,
        'items_por_dia': items_por_dia,
        'total_destinos': total_destinos,
        'total_dias': total_dias,
        'promedio_actividades_dia': round(promedio_actividades_dia, 1),
        'datos_grafico': json.dumps(datos_grafico),  # Convertir a JSON
    }
    return render(request, 'itinerarios/detalle_itinerario.html', context)


@login_required
def mis_itinerarios(request):
    """
    Lista de itinerarios del usuario con estadísticas
    """
    itinerarios = Itinerario.objects.filter(turista=request.user).order_by('-fecha_creacion')
    
    # Agregar estadísticas a cada itinerario
    for itinerario in itinerarios:
        itinerario.num_actividades = itinerario.items.count()
        itinerario.num_dias = itinerario.items.values('dia').distinct().count()
    
    context = {
        'itinerarios': itinerarios,
        'total_itinerarios': itinerarios.count(),
    }
    
    return render(request, 'itinerarios/mis_itinerarios.html', context)


@login_required
@require_POST
def agregar_actividad_rapida(request, itinerario_id):
    """
    API endpoint para agregar una actividad rápidamente al itinerario
    desde cualquier página (usando AJAX)
    """
    itinerario = get_object_or_404(Itinerario, id=itinerario_id, turista=request.user)
    actividad_id = request.POST.get('actividad_id')
    
    if not actividad_id:
        return JsonResponse({'success': False, 'error': 'No se especificó actividad'}, status=400)
    
    try:
        actividad = Actividad.objects.get(id=actividad_id, disponible=True)
        
        # Usar agregador inteligente
        agregador = AgregadorActividadesInteligente(itinerario)
        preferencias = request.user.preferencias.split(',') if hasattr(request.user, 'preferencias') else []
        
        item = agregador.agregar_actividad_auto(actividad, preferencias)
        
        return JsonResponse({
            'success': True,
            'message': f'Actividad "{actividad.nombre}" agregada al itinerario',
            'item_id': item.id,
            'dia': item.dia,
            'hora_inicio': item.hora_inicio.strftime('%H:%M'),
            'hora_fin': item.hora_fin.strftime('%H:%M'),
        })
        
    except Actividad.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Actividad no encontrada'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required
def eliminar_item(request, item_id):
    """
    Eliminar un item del itinerario y recalcular totales
    """
    item = get_object_or_404(ItemItinerario, id=item_id, itinerario__turista=request.user)
    itinerario = item.itinerario
    
    item.delete()
    
    # Recalcular totales
    itinerario.calcular_totales()
    
    messages.success(request, 'Actividad eliminada del itinerario')
    return redirect('itinerarios:detalle', itinerario_id=itinerario.id)


@login_required
def duplicar_itinerario(request, itinerario_id):
    """
    Duplicar un itinerario existente para modificarlo
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