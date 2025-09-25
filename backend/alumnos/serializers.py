from rest_framework import serializers # Importa los serializers de DRF
from .models import Alumno # Importa tu modelo 

class AlumnoSerializer(serializers.ModelSerializer): # Creamos un serializer para el modelo 

    class Meta:
        model = Alumno
        fields = [
            'id_alumno', 'nombre', 'apellido', 'dni', 'email', 'ciudad', 'direccion', 'telefono',
            'telefono_respaldo', 'inscripcion', 'fecha_nacimiento'
        ]
        read_only_fields = ['id_alumno']