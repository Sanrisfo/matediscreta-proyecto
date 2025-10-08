from django.urls import path
from . import views

app_name = 'tickets'

urlpatterns = [
    path('<int:ticket_id>/', views.detalle_ticket, name='detalle'),
    path('generar/<int:itinerario_id>/', views.generar_ticket, name='generar'),
]