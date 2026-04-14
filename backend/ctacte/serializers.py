from rest_framework import serializers
from .models import MesPago, MetodoPago, Pago, PagoDetalle


class MesPagoSerializer(serializers.ModelSerializer):
    class Meta:
        model = MesPago
        fields = ['id_mes', 'descripcion']
        read_only_fields = ['id_mes']


class MetodoPagoSerializer(serializers.ModelSerializer):
    class Meta:
        model = MetodoPago
        fields = ['id_metodo_pago', 'descripcion']
        read_only_fields = ['id_metodo_pago']


class PagoDetalleLiteSerializer(serializers.ModelSerializer):
    """Solo lectura — se usa para mostrar detalles dentro de un Pago (GET)."""
    mes_nombre     = serializers.CharField(source="mes.descripcion")
    carrera_nombre = serializers.CharField(source="carrera.descripcion")

    class Meta:
        model = PagoDetalle
        fields = [
            "id_detalle",
            "carrera",
            "carrera_nombre",
            "mes",
            "mes_nombre",
            "anio_pago",
            "id_concepto",
            "importe",
        ]


class PagoDetalleSerializer(serializers.ModelSerializer):
    """Escritura — para crear/editar detalles de pago individualmente."""
    class Meta:
        model = PagoDetalle
        fields = ['id_detalle', 'pago', 'carrera', 'mes', 'anio_pago', 'id_concepto', 'importe']
        read_only_fields = ['id_detalle']


class PagoReadSerializer(serializers.ModelSerializer):
    """
    Solo lectura — para GET de pagos.
    Muestra el nombre del método y los detalles anidados.
    """
    metodo       = serializers.CharField(source="id_metodo_pago.descripcion")
    alumno_nombre = serializers.SerializerMethodField()
    detalles     = PagoDetalleLiteSerializer(many=True, read_only=True)

    class Meta:
        model = Pago
        fields = [
            "id_pago",
            "id_alumno",
            "alumno_nombre",
            "fecha_pago",
            "importe_total",
            "metodo",
            "detalles",
        ]

    def get_alumno_nombre(self, obj):
        return str(obj.id_alumno) if obj.id_alumno else ""


class PagoWriteSerializer(serializers.ModelSerializer):
    """
    Escritura — para POST/PUT de la cabecera de un pago.
    Los detalles se crean por separado en RegistrarPago.
    """
    class Meta:
        model = Pago
        fields = [
            "id_pago",
            "id_alumno",
            "fecha_pago",
            "importe_total",
            "id_metodo_pago",
        ]
        read_only_fields = ["id_pago"]