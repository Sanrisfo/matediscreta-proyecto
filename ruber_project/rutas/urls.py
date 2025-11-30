from django.urls import path
from . import views

app_name = 'rutas'

urlpatterns = [
    path('mapa/', views.mapa_rutas, name='mapa_rutas'),
]