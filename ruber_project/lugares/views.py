from django.shortcuts import render, get_object_or_404
from django.contrib.auth import get_user_model
from django.db.models import Q
from .recomendations import obtener_recomendaciones
from .models import Destino, Categoria
from .red_black_tree import ordenar_destinos_rb


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


    #Arbol
    # Obtener parámetros de ordenamiento
    orden = request.GET.get('orden', 'nombre')  # Por defecto: alfabético
    direccion = request.GET.get('dir', 'asc')   # Por defecto: ascendente
    
    # Opciones válidas
    opciones_orden = {
        'nombre': 'nombre',
        'calificacion': 'calificacion',
        'precio': 'costo_entrada',
    }
    
    criterio = opciones_orden.get(orden, 'nombre')
    reverso = (direccion == 'desc')

    # Aplicar ordenamiento usando Árbol Rojo-Negro
    usar_rb_tree = request.GET.get('usar_rb', 'true') == 'true'

    if usar_rb_tree and destinos.exists():
        
        print(f"\n🌳 Usando Árbol Rojo-Negro para ordenar")
        print(f"   Criterio: {criterio}")
        print(f"   Dirección: {'Descendente' if reverso else 'Ascendente'}")
        
        # Ordenar usando árbol
        destinos_ordenados, arbol = ordenar_destinos_rb(destinos, criterio, reverso)
        
        # Convertir a lista (ya está ordenado)
        destinos = destinos_ordenados
        
        # Información del árbol para mostrar en template
        info_arbol = {
            'usado': True,
            'nodos': arbol.cantidad_nodos,
            'altura': arbol.altura(),
            'altura_maxima': 2 * (arbol.cantidad_nodos + 1).bit_length(),
            'criterio': criterio,
            'visualizacion': arbol.visualizar(),
        }

    print(destinos)
    # Debug: Imprimir información
    if isinstance(destinos, list):
        print(f"Total de destinos después de filtros: {len(destinos)}")
        if destinos:
            print(f"Primer destino: {destinos[0].nombre}")
    else:
        print(f"Total de destinos después de filtros: {destinos.count()}")
        if destinos.exists():
            print(f"Primer destino: {destinos.first().nombre}")

    
    context = {
        'destinos': destinos,
        'categorias': categorias,
        'categoria_actual': categoria_id,

        'preferencias_usuario': preferencias_usuario,

        'busqueda_actual': busqueda, 
        'orden_actual': orden,
        'direccion_actual': direccion,
        'info_arbol': info_arbol,
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