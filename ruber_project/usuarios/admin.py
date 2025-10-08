from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Turista

@admin.register(Turista)
class TuristaAdmin(UserAdmin):
    list_display = ['username', 'email', 'first_name', 'last_name', 'pais_origen', 'fecha_registro']
    list_filter = ['is_staff', 'is_active', 'fecha_registro', 'pais_origen']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    
    fieldsets = UserAdmin.fieldsets + (
        ('Información Turística', {
            'fields': ('telefono', 'pais_origen', 'foto_perfil', 'preferencias', 
                      'presupuesto_max', 'tiempo_disponible_dias')
        }),
    )