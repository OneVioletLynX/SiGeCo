from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from .models import MesPago,MetodoPago, Pago, PagoDetalle 

#1

class MesPagoSerializer(serializers.ModelSerializer):
    class Meta:
        model = MesPago
        fields = ['id_mes', 'descripcion']   # solo los campos reales
        read_only_fields = ['id_mes'] 
                
#2
        
class MetodoPagoSerializer(serializers.ModelSerializer):
    class Meta:
        model = MetodoPago
        fields = ['id_metodo_pago', 'descripcion']
        read_only_fields = ['id_metodo_pago']

#3

class PagoDetalleSerializer(serializers.ModelSerializer):
    class Meta:
        model = PagoDetalle
        fields = ['mes', 'importe']

class PagoDetalleLiteSerializer(serializers.ModelSerializer):
    mes = serializers.CharField(source="mes.descripcion")
    anio = serializers.IntegerField(source="anio_pago")
    pago_id = serializers.IntegerField(source="pago.id_pago")

    class Meta:
        model = PagoDetalle
        fields = [
            "carrera",
            "mes",
            "anio_pago",
            "importe"
        ]


class PagoSerializer(serializers.ModelSerializer):
    metodo = serializers.CharField(source="id_metodo_pago.descripcion")
    detalles = PagoDetalleLiteSerializer(many=True, read_only=True)

    class Meta:
        model = Pago
        fields = [
            "id_pago",
            "fecha_pago",
            "importe_total",
            "metodo",
            "detalles",
        ]


    def create(self, validated_data):
        detalles_data = validated_data.pop('detalles', [])
        pago = Pago.objects.create(**validated_data)
        for detalle_data in detalles_data:
            PagoDetalle.objects.create(pago=pago, **detalle_data)
        return pago
