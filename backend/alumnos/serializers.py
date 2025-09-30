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

    
# {
#   "id_alumno": 1,
#   "nombre": "Carlos",
#   "apellido": "Cáceres",
#   "dni": 40123456,
#   "email": "carlos@example.com",
#   "ciudad": "Marcos Juárez",
#   "direccion": "Av. Siempre Viva 742",
#   "telefono": 3511234567,
#   "telefono_respaldo": 3517654321,
#   "inscripcion": "2025-09-25",
#   "fecha_nacimiento": "2000-05-12"
# }
