from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from .models import Destino, Categoria

def lista_destinos(request):
    """Lista de destinos con filtros"""
    destinos = Destino.objects.filter(activo=True)
    
    # Filtros
    categoria_id = request.GET.get('categoria')
    busqueda = request.GET.get('q')
    preferencia = request.GET.get('preferencia')
    
    if categoria_id:
        destinos = destinos.filter(categoria_id=categoria_id)
    
    if busqueda:
        destinos = destinos.filter(
            Q(nombre__icontains=busqueda) | 
            Q(descripcion__icontains=busqueda)
        )
    
    if preferencia:
        # TODO: Filtrar por tags_preferencias (usar lógica de conjuntos)
        pass
    
    categorias = Categoria.objects.all()
    
    context = {
        'destinos': destinos,
        'categorias': categorias,
        'categoria_actual': categoria_id,
    }
    return render(request, 'lugares/lista_destinos.html', context)


def detalle_destino(request, destino_id):
    """Detalle de un destino con actividades"""
    destino = get_object_or_404(Destino, id=destino_id, activo=True)
    actividades = destino.actividades.filter(disponible=True)
    imagenes = destino.imagenes.all()
    
    context = {
        'destino': destino,
        'actividades': actividades,
        'imagenes': imagenes,
    }
    return render(request, 'lugares/detalle_destino.html', context)