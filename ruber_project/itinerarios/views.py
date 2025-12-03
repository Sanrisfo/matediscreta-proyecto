from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import Itinerario, ItemItinerario
from .forms import GenerarItinerarioForm, EditarItemForm
from .generators import GeneradorItinerarios, RegeneradorActividades
from lugares.models import Actividad, Destino
from datetime import datetime, timedelta
from decimal import Decimal
import json
import re

@login_required
def generar_itinerario(request):
    """
    Formulario para generar itinerario automático
    Usa preferencias y presupuesto del perfil del usuario
    """
    if request.method == 'POST':
        form = GenerarItinerarioForm(request.POST)
        if form.is_valid():
            datos = form.cleaned_data
            
            # Verificar que el usuario tenga preferencias configuradas
            if not request.user.preferencias:
                messages.warning(
                    request,
                    'Por favor configura tus preferencias en tu perfil antes de generar un itinerario.'
                )
                return redirect('usuarios:perfil')
            
            try:
                generador = GeneradorItinerarios(turista=request.user)
                itinerario = generador.generar(
                    nombre_itinerario=datos['nombre'],
                    fecha_inicio=datos['fecha_inicio'],
                    fecha_fin=datos['fecha_fin']
                )
                
                num_items = itinerario.items.count()
                
                if num_items > 0:
                    messages.success(
                        request, 
                        f'¡Itinerario "{itinerario.nombre}" generado con {num_items} actividades!'
                    )
                else:
                    messages.warning(
                        request,
                        'No se encontraron destinos que coincidan con tu perfil. Intenta ajustar tus preferencias o presupuesto.'
                    )
                
                return redirect('itinerarios:detalle', itinerario_id=itinerario.id)
                
            except Exception as e:
                messages.error(request, f'Error al generar itinerario: {str(e)}')
    else:
        # Pre-llenar con nombre sugerido
        fecha_actual = datetime.now().strftime('%d/%m/%Y')
        nombre_sugerido = f"Mi Itinerario {fecha_actual}"
        form = GenerarItinerarioForm(initial={'nombre': nombre_sugerido})
    
    # Información del perfil para mostrar
    perfil_info = {
        'tiene_preferencias': bool(request.user.preferencias),
        'preferencias': request.user.preferencias if request.user.preferencias else [],
        'presupuesto': request.user.presupuesto_max if request.user.presupuesto_max else 'Sin límite'
    }
    
    context = {
        'form': form,
        'perfil_info': perfil_info
    }
    return render(request, 'itinerarios/generar.html', context)


@login_required
def detalle_itinerario(request, itinerario_id):
    """
    Dashboard del itinerario con métricas REALES y alertas de presupuesto
    """
    itinerario = get_object_or_404(Itinerario, id=itinerario_id, turista=request.user)
    
    # Recalcular totales
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
    total_actividades = items.count()  # CORRECCIÓN: Variable correcta
    total_dias = len(items_por_dia) if items_por_dia else 1
    promedio_actividades_dia = total_actividades / total_dias if total_dias > 0 else 0
    
    # CRÍTICO: Verificar exceso de presupuesto
    presupuesto_usuario = request.user.presupuesto_max
    alerta_presupuesto = None
    
    if presupuesto_usuario:
        presupuesto_decimal = Decimal(str(presupuesto_usuario))
        costo_actual = itinerario.costo_total
        
        if costo_actual > presupuesto_decimal:
            exceso = costo_actual - presupuesto_decimal
            alerta_presupuesto = {
                'exceso': exceso,
                'presupuesto': presupuesto_decimal,
                'costo_actual': costo_actual,
                'porcentaje': int((costo_actual / presupuesto_decimal) * 100)
            }
    
    # Datos para gráficos
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
                    
                    if fin_dt < inicio_dt:
                        fin_dt += timedelta(days=1)
                    
                    tiempo_dia += (fin_dt - inicio_dt).seconds / 60
            
            # Calcular costo REAL del día
            costo_dia = 0
            for item in items_dia:
                costo_item = None
                
                if item.notas and 'Costo:' in item.notas:
                    try:
                        match = re.search(r'S/\s*(\d+\.?\d*)', item.notas)
                        if match:
                            costo_item = float(match.group(1))
                    except:
                        pass
                
                if costo_item is None:
                    costo_item = float(item.destino.costo_entrada)
                
                costo_dia += costo_item
            
            datos_grafico['dias'].append(f'Día {dia}')
            datos_grafico['actividades'].append(len(items_dia))
            datos_grafico['tiempo'].append(int(tiempo_dia))
            datos_grafico['costo'].append(round(costo_dia, 2))
    else:
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
        'total_actividades': total_actividades,  # CORRECCIÓN
        'total_dias': total_dias,
        'promedio_actividades_dia': round(promedio_actividades_dia, 1),
        'datos_grafico': json.dumps(datos_grafico),
        'alerta_presupuesto': alerta_presupuesto,  # NUEVO
    }
    return render(request, 'itinerarios/detalle_itinerario.html', context)


@login_required
def regenerar_actividades(request, itinerario_id):
    """Regenera 3 actividades respetando el presupuesto"""
    itinerario = get_object_or_404(Itinerario, id=itinerario_id, turista=request.user)
    
    try:
        regenerador = RegeneradorActividades(itinerario)
        regenerador.regenerar_3_actividades()
        
        messages.success(request, '¡3 nuevas actividades generadas respetando tu presupuesto!')
        
    except Exception as e:
        messages.error(request, f'Error al regenerar actividades: {str(e)}')
    
    return redirect('itinerarios:detalle', itinerario_id=itinerario.id)


@login_required
def mis_itinerarios(request):
    """Lista de itinerarios del usuario"""
    itinerarios = Itinerario.objects.filter(turista=request.user).order_by('-fecha_creacion')
    
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
    """Eliminar un item del itinerario"""
    item = get_object_or_404(ItemItinerario, id=item_id, itinerario__turista=request.user)
    itinerario = item.itinerario
    
    item.delete()
    itinerario.calcular_totales()
    
    messages.success(request, 'Actividad eliminada del itinerario')
    return redirect('itinerarios:detalle', itinerario_id=itinerario.id)


@login_required
def eliminar_itinerario(request, itinerario_id):
    """Eliminar un itinerario completo"""
    itinerario = get_object_or_404(Itinerario, id=itinerario_id, turista=request.user)
    
    nombre = itinerario.nombre
    itinerario.delete()
    
    messages.success(request, f'Itinerario "{nombre}" eliminado exitosamente')
    return redirect('itinerarios:mis_itinerarios')


@login_required
def duplicar_itinerario(request, itinerario_id):
    """Duplicar un itinerario existente"""
    itinerario_original = get_object_or_404(Itinerario, id=itinerario_id, turista=request.user)
    
    itinerario_nuevo = Itinerario.objects.create(
        turista=request.user,
        nombre=f"{itinerario_original.nombre} (Copia)",
        descripcion=itinerario_original.descripcion,
        fecha_inicio=itinerario_original.fecha_inicio,
        fecha_fin=itinerario_original.fecha_fin,
        estado='borrador'
    )
    
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
    
    itinerario_nuevo.calcular_totales()
    
    messages.success(request, 'Itinerario duplicado exitosamente')
    return redirect('itinerarios:detalle', itinerario_id=itinerario_nuevo.id)


# ============================================
# NUEVAS FUNCIONALIDADES
# ============================================

@login_required
@require_POST
def agregar_destino_a_itinerario(request, destino_id):
    """
    Agrega un destino (con su mejor actividad) a un itinerario existente
    """
    destino = get_object_or_404(Destino, id=destino_id, activo=True)
    itinerario_id = request.POST.get('itinerario_id')
    
    if not itinerario_id:
        messages.error(request, 'Debes seleccionar un itinerario')
        return redirect('lugares:detalle_destino', destino_id=destino_id)
    
    itinerario = get_object_or_404(Itinerario, id=itinerario_id, turista=request.user)
    
    # Verificar presupuesto
    presupuesto_usuario = request.user.presupuesto_max
    
    # Seleccionar mejor actividad
    actividades = destino.actividades.filter(disponible=True).order_by('costo')
    
    if actividades.exists():
        actividad = actividades.first()
        costo = actividad.costo
        duracion = actividad.duracion_minutos
        notas = f" Actividad: {actividad.nombre}\n Duración: {duracion} min\n Costo: S/ {costo}"
    else:
        costo = destino.costo_entrada if destino.costo_entrada else Decimal('20.00')
        duracion = 90
        notas = f" Visita libre\n Duración: {duracion} min\n     Costo: S/ {costo}"
    
    # Verificar presupuesto
    costo_futuro = itinerario.costo_total + Decimal(str(costo))
    
    if presupuesto_usuario and costo_futuro > Decimal(str(presupuesto_usuario)):
        exceso = costo_futuro - Decimal(str(presupuesto_usuario))
        messages.warning(
            request,
            f'⚠️ Agregar esta actividad excederá tu presupuesto por S/ {exceso}. ¿Deseas continuar de todos modos?'
        )
    
    # Calcular orden y horarios
    ultimo_item = itinerario.items.order_by('-orden').first()
    
    if ultimo_item:
        nuevo_orden = ultimo_item.orden + 1
        nuevo_dia = ultimo_item.dia
        
        # Calcular nueva hora
        hora_fin_anterior = datetime.combine(datetime.today(), ultimo_item.hora_fin)
        nueva_hora_inicio = (hora_fin_anterior + timedelta(minutes=30)).time()
    else:
        nuevo_orden = 1
        nuevo_dia = 1
        nueva_hora_inicio = datetime.strptime('09:00', '%H:%M').time()
    
    nueva_hora_fin = (datetime.combine(datetime.today(), nueva_hora_inicio) + timedelta(minutes=duracion)).time()
    
    # Crear item
    ItemItinerario.objects.create(
        itinerario=itinerario,
        destino=destino,
        orden=nuevo_orden,
        dia=nuevo_dia,
        hora_inicio=nueva_hora_inicio,
        hora_fin=nueva_hora_fin,
        notas=notas
    )
    
    # Recalcular totales
    itinerario.calcular_totales()
    
    messages.success(request, f'✅ {destino.nombre} agregado a "{itinerario.nombre}"')
    return redirect('itinerarios:detalle', itinerario_id=itinerario.id)


@login_required
def editar_item(request, item_id):
    """
    Edita el día y horarios de un item del itinerario
    """
    item = get_object_or_404(ItemItinerario, id=item_id, itinerario__turista=request.user)
    
    if request.method == 'POST':
        form = EditarItemForm(request.POST, instance=item)
        if form.is_valid():
            form.save()
            
            # Recalcular totales
            item.itinerario.calcular_totales()
            
            messages.success(request, f'✅ Actividad "{item.destino.nombre}" actualizada')
            return redirect('itinerarios:detalle', itinerario_id=item.itinerario.id)
    else:
        form = EditarItemForm(instance=item)
    
    context = {
        'form': form,
        'item': item
    }
    return render(request, 'itinerarios/editar_item.html', context)


@login_required
@require_POST
def editar_item_ajax(request, item_id):
    """
    Versión AJAX para editar item (para modal)
    """
    item = get_object_or_404(ItemItinerario, id=item_id, itinerario__turista=request.user)
    
    form = EditarItemForm(request.POST, instance=item)
    if form.is_valid():
        form.save()
        item.itinerario.calcular_totales()
        
        return JsonResponse({
            'success': True,
            'message': 'Actividad actualizada correctamente'
        })
    else:
        return JsonResponse({
            'success': False,
            'errors': form.errors
        }, status=400)
    
@login_required
@require_POST
def agregar_actividad_manual(request, actividad_id):
    """
    CORREGIDO: Agrega una actividad específica a un itinerario
    Funciona desde cualquier vista (lista o detalle)
    """
    actividad = get_object_or_404(Actividad, id=actividad_id, disponible=True)
    itinerario_id = request.POST.get("itinerario")  # CAMBIO: usar 'itinerario' en lugar de 'itinerario_id'
    
    if not itinerario_id:
        messages.error(request, "⚠️ Debes seleccionar un itinerario válido.")
        return redirect("lugares:detalle_destino", destino_id=actividad.destino.id)

    try:
        itinerario = get_object_or_404(Itinerario, id=int(itinerario_id), turista=request.user)
    except (ValueError, Itinerario.DoesNotExist):
        messages.error(request, "❌ El itinerario seleccionado no existe.")
        return redirect("lugares:detalle_destino", destino_id=actividad.destino.id)

    # Obtener último item del itinerario
    ultimo = itinerario.items.order_by("-orden").first()

    if ultimo:
        orden = ultimo.orden + 1
        dia = ultimo.dia
        hora_inicio = (datetime.combine(datetime.today(), ultimo.hora_fin) + timedelta(minutes=30)).time()
    else:
        orden = 1
        dia = 1
        hora_inicio = datetime.strptime("09:00", "%H:%M").time()

    # Calcular hora fin
    duracion = actividad.duracion_minutos if actividad.duracion_minutos else 90
    hora_fin = (
        datetime.combine(datetime.today(), hora_inicio) +
        timedelta(minutes=duracion)
    ).time()

    # Crear el item
    ItemItinerario.objects.create(
        itinerario=itinerario,
        destino=actividad.destino,
        orden=orden,
        dia=dia,
        hora_inicio=hora_inicio,
        hora_fin=hora_fin,
        notas=f" Actividad: {actividad.nombre}\n Costo: S/ {actividad.costo}\n Duración: {duracion} min\n {actividad.descripcion[:100] if actividad.descripcion else 'Sin descripción'}"
    )

    # Recalcular totales
    itinerario.calcular_totales()

    messages.success(request, f"✅ La actividad '{actividad.nombre}' fue agregada a '{itinerario.nombre}'.")
    
    # CORREGIDO: Redirigir al detalle del itinerario
    return redirect("itinerarios:detalle", itinerario_id=itinerario.id)