from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Itinerario, ItemItinerario
from .forms import GenerarItinerarioForm
from .generators import GeneradorItinerarios

@login_required
def generar_itinerario(request):
    """
    Formulario para generar itinerario automático
    """
    if request.method == 'POST':
        form = GenerarItinerarioForm(request.POST)
        if form.is_valid():
            # Extraer datos del formulario
            datos = form.cleaned_data
            
            # Generar itinerario usando el algoritmo
            generador = GeneradorItinerarios(turista=request.user)
            itinerario = generador.generar(
                fecha_inicio=datos['fecha_inicio'],
                fecha_fin=datos['fecha_fin'],
                preferencias=datos['preferencias'],
                presupuesto_max=datos['presupuesto_max']
            )
            
            messages.success(request, '¡Itinerario generado exitosamente!')
            return redirect('itinerarios:detalle', itinerario_id=itinerario.id)
    else:
        form = GenerarItinerarioForm()
    
    return render(request, 'itinerarios/generar.html', {'form': form})


@login_required
def detalle_itinerario(request, itinerario_id):
    """
    Ver detalle de un itinerario
    """
    itinerario = get_object_or_404(Itinerario, id=itinerario_id, turista=request.user)
    items = itinerario.items.all().select_related('destino')
    
    context = {
        'itinerario': itinerario,
        'items': items,
    }
    return render(request, 'itinerarios/detalle_itinerario.html', context)


@login_required
def mis_itinerarios(request):
    """
    Lista de itinerarios del usuario
    """
    itinerarios = Itinerario.objects.filter(turista=request.user)
    
    return render(request, 'itinerarios/mis_itinerarios.html', {'itinerarios': itinerarios})

