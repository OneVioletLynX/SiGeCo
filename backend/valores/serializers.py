from rest_framework import serializers
from .models import Valor, Concepto


class ConceptoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Concepto
        fields = ["id_concepto", "descripcion"]
        read_only_fields = ["id_concepto"]


class ValorSerializer(serializers.ModelSerializer):
    id_carrera_nombre = serializers.CharField(source="id_carrera.descripcion", read_only=True)
    id_concepto_nombre = serializers.CharField(source="id_concepto.descripcion", read_only=True)

    class Meta:
        model = Valor
        fields = [
            "id_valor",
            "id_carrera",
            "id_carrera_nombre",
            "id_concepto",
            "id_concepto_nombre",
            "fecha_inicio",
            "fecha_fin",
            "importe"
        ]
        read_only_fields = ["id_valor"]
