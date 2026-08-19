from rest_framework import serializers
from .models import Carrera, CarreraCursada, Estado
from valores.models import Valor, Concepto
from django.utils import timezone
from alumnos.models import Alumno



class CarreraSerializer(serializers.ModelSerializer):
    # Campos que vienen del form (HTML)
    inscripcion = serializers.DecimalField(max_digits=10, decimal_places=2, write_only=True, required=False)
    cuota = serializers.DecimalField(max_digits=10, decimal_places=2, write_only=True, required=False)
    id_estado = serializers.PrimaryKeyRelatedField(queryset=Estado.objects.all(), required=False)

    # Campos calculados (solo lectura)
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
            "id_carrera",
            "descripcion",
            "id_estado",
            "estado_actual",
            "inscripcion",
            "cuota",
            "inscripcion_vigente",
            "cuota_vigente",
            "total_alumnos",
            "activos",
            "finalizados",
            "inactivos",
            "color",
        ]

    # -------------------------------------------------------
    # Obtener valores vigentes (usa fecha_inicio en lugar de modificacion)
    # -------------------------------------------------------
    def get_inscripcion_vigente(self, obj):
        concepto = Concepto.objects.filter(descripcion__iexact="Inscripción").first()
        if not concepto:
            return None
        valor = Valor.objects.filter(id_carrera=obj, id_concepto=concepto).order_by("-fecha_inicio").first()
        return valor.importe if valor else None

    def get_cuota_vigente(self, obj):
        concepto = Concepto.objects.filter(descripcion__iexact="Importe cuota").first()
        if not concepto:
            return None
        valor = Valor.objects.filter(id_carrera=obj, id_concepto=concepto).order_by("-fecha_inicio").first()
        return valor.importe if valor else None

    # -------------------------------------------------------
    # Crear carrera + valores de inscripción y cuota
    # -------------------------------------------------------
    def create(self, validated_data):
        inscripcion = validated_data.pop("inscripcion", None)
        cuota = validated_data.pop("cuota", None)
        carrera = Carrera.objects.create(**validated_data)

        concepto_insc, _ = Concepto.objects.get_or_create(
            descripcion__iexact="Inscripción", defaults={"descripcion": "Inscripción"}
        )
        concepto_cuota, _ = Concepto.objects.get_or_create(
            descripcion__iexact="Importe cuota", defaults={"descripcion": "Importe cuota"}
        )

        if inscripcion is not None:
            Valor.objects.create(
                id_carrera=carrera,
                id_concepto=concepto_insc,
                fecha_inicio=timezone.now(),
                importe=inscripcion,
            )
        if cuota is not None:
            Valor.objects.create(
                id_carrera=carrera,
                id_concepto=concepto_cuota,
                fecha_inicio=timezone.now(),
                importe=cuota,
            )

        return carrera

    # -------------------------------------------------------
    # Actualizar carrera (si cambian valores, se crea nuevo registro Valor)
    # -------------------------------------------------------
    def update(self, instance, validated_data):
        inscripcion = validated_data.pop("inscripcion", None)
        cuota = validated_data.pop("cuota", None)
        instance = super().update(instance, validated_data)

        concepto_insc = Concepto.objects.filter(descripcion__iexact="Inscripción").first()
        concepto_cuota = Concepto.objects.filter(descripcion__iexact="Importe cuota").first()

        if inscripcion is not None and concepto_insc:
            Valor.objects.create(
                id_carrera=instance,
                id_concepto=concepto_insc,
                fecha_inicio=timezone.now(),
                importe=inscripcion,
            )
        if cuota is not None and concepto_cuota:
            Valor.objects.create(
                id_carrera=instance,
                id_concepto=concepto_cuota,
                fecha_inicio=timezone.now(),
                importe=cuota,
            )

        return instance

    # -------------------------------------------------------
    # Contadores de alumnos por estado
    # -------------------------------------------------------
    def get_total_alumnos(self, obj):
        return CarreraCursada.objects.filter(carrera=obj).count()

    def get_activos(self, obj):
        return CarreraCursada.objects.filter(carrera=obj, id_estado__descripcion__iexact="Activo").count()

    def get_finalizados(self, obj):
        return CarreraCursada.objects.filter(carrera=obj, id_estado__descripcion__iexact="Finalizado").count()

    def get_inactivos(self, obj):
        return CarreraCursada.objects.filter(carrera=obj, id_estado__descripcion__iexact="Inactivo").count()


class CarrerasCursadasSerializer(serializers.ModelSerializer):

    # Lectura
    alumno_id  = serializers.IntegerField(source="alumno.id_alumno",    read_only=True)
    carrera_id = serializers.IntegerField(source="carrera.id_carrera",  read_only=True)
    estado_id  = serializers.IntegerField(source="id_estado.id_estado", read_only=True)

    # Escritura
    alumno       = serializers.PrimaryKeyRelatedField(queryset=Alumno.objects.all(),   write_only=True)
    carrera      = serializers.PrimaryKeyRelatedField(queryset=Carrera.objects.all(),  write_only=True)
    id_estado    = serializers.PrimaryKeyRelatedField(queryset=Estado.objects.all(),   write_only=True, required=False)
    anio_ingreso = serializers.IntegerField(write_only=True, required=False)

    class Meta:
        model  = CarreraCursada
        fields = ["alumno_id", "carrera_id", "estado_id", "alumno", "carrera", "id_estado", "anio_ingreso"]

    def create(self, validated_data):
        anio_ingreso = validated_data.pop("anio_ingreso", None)
        estado       = validated_data.pop("id_estado",    None) or Estado.objects.get(id_estado=1)

        return CarreraCursada.objects.create(
            alumno=validated_data["alumno"],
            carrera=validated_data["carrera"],
            id_estado=estado,
            anio_ingreso=anio_ingreso,
        )
    
class EstadoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Estado
        fields = ['id_estado', 'descripcion']
        read_only_fields = ['id_estado']