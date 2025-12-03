from django.urls import path
from . import views

app_name = 'itinerarios'

urlpatterns = [
    # Generación de itinerarios
    path('generar/', views.generar_itinerario, name='generar'),
    
    # Visualización
    path('<int:itinerario_id>/', views.detalle_itinerario, name='detalle'),
    path('mis-itinerarios/', views.mis_itinerarios, name='mis_itinerarios'),
    
    # Acciones sobre itinerarios
    path('<int:itinerario_id>/regenerar/', views.regenerar_actividades, name='regenerar'),
    path('<int:itinerario_id>/duplicar/', views.duplicar_itinerario, name='duplicar'),
    path('<int:itinerario_id>/eliminar/', views.eliminar_itinerario, name='eliminar'),
    
    # Acciones sobre items
    path('item/<int:item_id>/eliminar/', views.eliminar_item, name='eliminar_item'),
]