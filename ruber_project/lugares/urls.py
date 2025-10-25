from django.urls import path
from . import views

app_name = 'lugares'

urlpatterns = [
    path('', views.lista_destinos, name='lista_destinos'),
    path('<int:destino_id>/', views.detalle_destino, name='detalle_destino'),
    
]