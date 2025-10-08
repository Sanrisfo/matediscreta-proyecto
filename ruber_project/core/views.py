from django.shortcuts import render
from lugares.models import Destino, Categoria

def home(request):
    """Página principal con búsqueda"""
    destinos_destacados = Destino.objects.filter(activo=True).order_by('-calificacion')[:6]
    categorias = Categoria.objects.all()
    
    context = {
        'destinos_destacados': destinos_destacados,
        'categorias': categorias,
    }
    return render(request, 'core/home.html', context)