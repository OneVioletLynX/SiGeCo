from rest_framework import serializers
from .models import Carrera, CarreraCursada, Estado
from valores.models import Valor, Concepto
from django.utils import timezone

class CarreraSerializer(serializers.ModelSerializer):
    # Campos de entrada
    inscripcion = serializers.DecimalField(max_digits=10, decimal_places=2, write_only=True, required=False)
    cuota = serializers.DecimalField(max_digits=10, decimal_places=2, write_only=True, required=False)
    id_estado = serializers.PrimaryKeyRelatedField(queryset=Estado.objects.all(), required=False)

    # Campos de salida (solo lectura)
    inscripcion_vigente = serializers.SerializerMethodField()
    cuota_vigente = serializers.SerializerMethodField()
    estado_actual = serializers.CharField(source="id_estado.descripcion", read_only=True)
    total_alumnos = serializers.SerializerMethodField()
    activos = serializers.SerializerMethodField()
    finalizados = serializers.SerializerMethodField()
    inactivos = serializers.SerializerMethodField()

    class Meta:
        model = Carrera
        fields = [
            'id_carrera',
            'descripcion',
            'id_estado',
            'estado_actual',
            'inscripcion',
            'cuota',
            'inscripcion_vigente',
            'cuota_vigente',
            'total_alumnos',
            'activos',
            'finalizados',
            'inactivos',
        ]

    # --------------------------
    # Valores vigentes
    # --------------------------
    def get_inscripcion_vigente(self, obj):
        concepto = Concepto.objects.filter(descripcion__iexact='Inscripción').first()
        if not concepto:
            return None
        valor = Valor.objects.filter(id_carrera=obj, id_concepto=concepto).order_by('-modificacion').first()
        return valor.importe if valor else None

    def get_cuota_vigente(self, obj):
        concepto = Concepto.objects.filter(descripcion__iexact='Cuota').first()
        if not concepto:
            return None
        valor = Valor.objects.filter(id_carrera=obj, id_concepto=concepto).order_by('-modificacion').first()
        return valor.importe if valor else None

    # --------------------------
    # Estado y totales
    # --------------------------
    def get_estado_actual(self, obj):
        # Si querés que las carreras tengan su propio estado, podés extender esto.
        # Por ahora, devolvemos "Activa" si tiene alumnos activos.
        activos = CarreraCursada.objects.filter(carrera=obj, id_estado__descripcion__iexact="Activo").count()
        finalizados = CarreraCursada.objects.filter(carrera=obj, id_estado__descripcion__iexact="Finalizado").count()
        inactivos = CarreraCursada.objects.filter(carrera=obj, id_estado__descripcion__iexact="Inactivo").count()
        if activos:
            return "Activa"
        elif finalizados and not activos:
            return "Finalizada"
        elif inactivos and not (activos or finalizados):
            return "Inactiva"
        return "Sin alumnos"

    def get_total_alumnos(self, obj):
        return CarreraCursada.objects.filter(carrera=obj).count()

    def get_activos(self, obj):
        return CarreraCursada.objects.filter(carrera=obj, id_estado__descripcion__iexact="Activo").count()

    def get_finalizados(self, obj):
        return CarreraCursada.objects.filter(carrera=obj, id_estado__descripcion__iexact="Finalizado").count()

    def get_inactivos(self, obj):
        return CarreraCursada.objects.filter(carrera=obj, id_estado__descripcion__iexact="Inactivo").count()

    # --------------------------
    # Creación y actualización (igual que antes)
    # --------------------------
    def create(self, validated_data):
        inscripcion = validated_data.pop('inscripcion', None)
        cuota = validated_data.pop('cuota', None)
        carrera = Carrera.objects.create(**validated_data)

        concepto_insc, _ = Concepto.objects.get_or_create(descripcion__iexact='Inscripción', defaults={'descripcion': 'Inscripción'})
        concepto_cuota, _ = Concepto.objects.get_or_create(descripcion__iexact='Cuota', defaults={'descripcion': 'Cuota'})

        if inscripcion is not None:
            Valor.objects.create(id_carrera=carrera, id_concepto=concepto_insc, importe=inscripcion, modificacion=timezone.now())
        if cuota is not None:
            Valor.objects.create(id_carrera=carrera, id_concepto=concepto_cuota, importe=cuota, modificacion=timezone.now())
        return carrera

    def update(self, instance, validated_data):
        inscripcion = validated_data.pop('inscripcion', None)
        cuota = validated_data.pop('cuota', None)
        instance = super().update(instance, validated_data)

        concepto_insc, _ = Concepto.objects.get_or_create(descripcion__iexact='Inscripción', defaults={'descripcion': 'Inscripción'})
        concepto_cuota, _ = Concepto.objects.get_or_create(descripcion__iexact='Cuota', defaults={'descripcion': 'Cuota'})

        if inscripcion is not None:
            valor_insc = Valor.objects.filter(id_carrera=instance, id_concepto=concepto_insc).order_by('-modificacion').first()
            if valor_insc:
                valor_insc.importe = inscripcion
                valor_insc.modificacion = timezone.now()
                valor_insc.save()
        if cuota is not None:
            valor_cuota = Valor.objects.filter(id_carrera=instance, id_concepto=concepto_cuota).order_by('-modificacion').first()
            if valor_cuota:
                valor_cuota.importe = cuota
                valor_cuota.modificacion = timezone.now()
                valor_cuota.save()

        return instance


    # ---------------------------------------------------
    # Métodos de solo lectura (mostrar valores vigentes)
    # ---------------------------------------------------
    def get_inscripcion_vigente(self, obj):
        concepto = Concepto.objects.filter(descripcion__iexact='Inscripción').first()
        if not concepto:
            return None
        valor = Valor.objects.filter(id_carrera=obj, id_concepto=concepto).order_by('-modificacion').first()
        return valor.importe if valor else None

    def get_cuota_vigente(self, obj):
        concepto = Concepto.objects.filter(descripcion__iexact='Cuota').first()
        if not concepto:
            return None
        valor = Valor.objects.filter(id_carrera=obj, id_concepto=concepto).order_by('-modificacion').first()
        return valor.importe if valor else None


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