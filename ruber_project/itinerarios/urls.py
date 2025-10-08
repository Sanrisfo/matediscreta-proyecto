from django.urls import path
from . import views

app_name = 'itinerarios'

urlpatterns = [
    path('generar/', views.generar_itinerario, name='generar'),
    path('<int:itinerario_id>/', views.detalle_itinerario, name='detalle'),
    path('mis-itinerarios/', views.mis_itinerarios, name='mis_itinerarios'),
]