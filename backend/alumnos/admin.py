from django.contrib import admin
from .models import Alumno

@admin.register(Alumno)
class AlumnoAdmin(admin.ModelAdmin):
    list_display  = ('id_alumno', 'apellido', 'nombre', 'dni')   # sacá 'legajo' si no existe
    search_fields = ('apellido', 'nombre', 'dni', 'id')
    list_filter   = ()  # o ('ciudad',) si ese campo existe en tu modelo
