from django.shortcuts import render, get_object_or_404
from django.contrib.auth import get_user_model
from django.db.models import Q
from .models import Destino, Categoria


def lista_destinos(request):
    """Lista de destinos con filtros"""
    destinos = Destino.objects.filter(activo=True)
    
    print(request.user.username)
    print(request.user.preferencias)
    preferencias_usuario=request.user.preferencias
    A=[]
    
    
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
    
    if preferencia and preferencias_usuario:
        for e in preferencias_usuario:
            for i in destinos:
                if e in i.tags_preferencias:
                    A.append(i.nombre)
                    
        pref=Destino.objects.none()
        for e in A:
            pref = pref | Destino.objects.filter(nombre=e)

        print(pref)
        destinos=pref

    print(A)
    categorias = Categoria.objects.all()
    print(destinos)
    
    print(destinos.last().tags_preferencias)
    print(destinos[0].descripcion)
    print(destinos[0].nombre)

    context = {
        'destinos': destinos,
        'categorias': categorias,
        'categoria_actual': categoria_id,
        'preferencias_usuario': preferencias_usuario,
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