from rest_framework import serializers
from .models import Carrera, CarreraCursada, Estado

class CarreraSerializer(serializers.ModelSerializer):
    class Meta:
        model = Carrera
        fields = ['id_carrera', 'descripcion']
        read_only_fields = ['id_carrera']

{
  "descripcion": "Ingeniería en Sistemas"
}

class CarrerasCursadasSerializer(serializers.ModelSerializer):
    alumno_id = serializers.IntegerField(source="alumno.id_alumno", read_only=True)
    carrera_id = serializers.IntegerField(source="carrera.id_carrera", read_only=True)
    estado_id = serializers.IntegerField(source="id_estado.id_estado", read_only=True)

    class Meta:
        model = CarreraCursada
        fields = ["alumno_id", "carrera_id", "estado_id"]
    
class EstadoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Estado
        fields = ['id_estado', 'descripcion']
        read_only_fields = ['id_estado']