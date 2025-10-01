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

class PagoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pago
        fields = [
            'id_pago',
            'id_alumno',
            'fecha_pago',
            'importe_total',
            'id_metodo_pago',
            'id_usuario',
        ]
        read_only_fields = ['id_pago']
        
#4  
      
class PagoDetalleSerializer(serializers.ModelSerializer):
    id_pago = serializers.IntegerField(source='pago_id')
    id_mes  = serializers.IntegerField(source='mes_id')

    class Meta:
        model = PagoDetalle
        fields = ['id_detalle', 'id_pago', 'id_mes', 'importe']
        read_only_fields = ['id_detalle']