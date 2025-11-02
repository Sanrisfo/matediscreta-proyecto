from django.shortcuts import render, get_object_or_404
from django.contrib.auth import get_user_model
from django.db.models import Q
from .recomendations import obtener_recomendaciones
from .models import Destino, Categoria


def lista_destinos(request):
    """Lista de destinos con filtros"""
    destinos = Destino.objects.filter(activo=True)
    
    # --- CAMBIOS AQUI ---
    preferencias_usuario = [] # Inicializamos como lista vacía por defecto
    
    if request.user.is_authenticated:
        print(request.user.username)
        preferencias_usuario = request.user.preferencias
    else:
        print("Usuario no logueado (Anónimo)")
    # --- FIN CAMBIOS ---

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

    # Calcular información adicional
    costo_total_actividades = sum(act.costo for act in actividades)
    tiempo_total_actividades = sum(act.duracion_minutos for act in actividades)
    
    print(f" 1) {costo_total_actividades}")
    print(f" 2) {tiempo_total_actividades}")
    
    recomendaciones=obtener_recomendaciones(destino,5)

    print(f"Mostrando detalle de: {destino.nombre}")
    print(f"Actividades disponibles: {actividades.count()}")
    print(f"Imágenes en galería: {imagenes.count()}")
    print(f"Recomendaciones generadas: {len(recomendaciones)}")
    print(recomendaciones)



    context = {
        'destino': destino,
        'actividades': actividades,
        'imagenes': imagenes,

        'costo_total_actividades': costo_total_actividades,
        'tiempo_total_actividades': tiempo_total_actividades,
        'recomendaciones': recomendaciones,
    }
    return render(request, 'lugares/detalle_destino.html', context)