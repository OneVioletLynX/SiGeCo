from rest_framework import serializers # Importa los serializers de DRF
from .models import Valor, Concepto # Importa tu modelo 

class ValoresSerializer(serializers.ModelSerializer): # Creamos un serializer para el modelo 

    class Meta:
        model = Valor
        fields = [
            'id_valor', 'id_carrera', 'id_concepto', 'modificacion', 'importe'
        ]
        read_only_fields = ['id_valor']

class ConceptoSerializer(serializers.ModelSerializer): # Creamos un serializer para el modelo 
    class Meta:
        model = Concepto
        fields = [
            'id_concepto', 'descripcion'
        ]
        read_only_fields = ['id_concepto']