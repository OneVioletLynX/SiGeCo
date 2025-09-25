from rest_framework import serializers
from .models import Carrera, CarreraCursada, Estado

class CarreraSerializer(serializers.ModelSerializer):
    class Meta:
        model = Carrera
        fields = ['id_carrera', 'descripcion']
        read_only_fields = ['id_carrera']

class CarrerasCursadasSerializer(serializers.ModelSerializer):
    class Meta:
        model = CarreraCursada
        fields = ['id_alumno', 'id_carrera', 'id_estado']
        read_only_fields = ['id_alumno', 'id_carrera', 'id_estado']
    
class EstadoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Estado
        fields = ['id_estado', 'descripcion']
        read_only_fields = ['id_estado']