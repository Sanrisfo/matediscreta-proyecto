from django.contrib import admin
from .models import Ticket

@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ['codigo', 'itinerario', 'estado', 'fecha_emision', 'fecha_validez']
    list_filter = ['estado', 'fecha_emision', 'fecha_validez']
    search_fields = ['codigo', 'itinerario__nombre']
    readonly_fields = ['codigo', 'fecha_emision']
    
    fieldsets = (
        ('Información del Ticket', {
            'fields': ('itinerario', 'codigo', 'codigo_qr')
        }),
        ('Fechas', {
            'fields': ('fecha_emision', 'fecha_validez')
        }),
        ('Estado y Validación', {
            'fields': ('estado', 'fecha_uso', 'validado_por')
        }),
    )