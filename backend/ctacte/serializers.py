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

class PagoSerializer(serializers.ModelSerializer):
    detalles = PagoDetalleSerializer(many=True, write_only=True, required=False)
    detalles_info = PagoDetalleSerializer(source='pagodetalle_set', many=True, read_only=True)

    class Meta:
        model = Pago
        fields = [
            'id_pago',
            'id_alumno',
            'fecha_pago',
            'importe_total',
            'id_metodo_pago',
            'detalles',        # para crear
            'detalles_info',   # para ver
        ]
        read_only_fields = ['id_pago']

    def create(self, validated_data):
        detalles_data = validated_data.pop('detalles', [])
        pago = Pago.objects.create(**validated_data)
        for detalle_data in detalles_data:
            PagoDetalle.objects.create(pago=pago, **detalle_data)
        return pago
