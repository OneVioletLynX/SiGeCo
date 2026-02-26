from rest_framework import serializers
from .models import Provincia, Localidad


class ProvinciaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Provincia
        fields = ["id_prov", "nombre"]


class LocalidadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Localidad
        fields = ["id_loc", "nombre"]