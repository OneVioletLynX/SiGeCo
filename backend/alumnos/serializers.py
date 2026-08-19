from django.db import transaction
from rest_framework import serializers
from .models import Alumno
from carreras.models import CarreraCursada


class AlumnoSerializer(serializers.ModelSerializer):

    # --------- WRITE ONLY (desde el form) ----------
    id_carrera   = serializers.IntegerField(write_only=True, required=False)
    id_estado    = serializers.IntegerField(write_only=True, required=False)
    anio_ingreso = serializers.IntegerField(write_only=True, required=False)

    # --------- READ ONLY ----------
    # Campos legacy (primera carrera) — se mantienen para no romper otras vistas
    carrera_actual = serializers.SerializerMethodField()
    estado_actual  = serializers.SerializerMethodField()
    carrera_nombre = serializers.SerializerMethodField()
    estado_nombre  = serializers.SerializerMethodField()
    carrera_color  = serializers.SerializerMethodField()

    # NUEVO: lista completa de carreras del alumno
    carreras = serializers.SerializerMethodField()

    class Meta:
        model = Alumno
        fields = [
            'id_alumno',
            'legajo',
            'nombre',
            'apellido',
            'fecha_nacimiento',
            'dni',
            'cuit',
            'ciudad',
            'direccion',
            'numero',
            'prefijo',
            'telefono',
            'email',

            # write
            'id_carrera',
            'id_estado',
            'anio_ingreso',

            # read — primera carrera (legacy)
            'carrera_actual',
            'estado_actual',
            'carrera_nombre',
            'estado_nombre',
            'carrera_color',

            # read — todas las carreras
            'carreras',
        ]

    # --------------------------------------------------
    # Helper — primera carrera (para campos legacy)
    # Usa la caché del prefetch_related para evitar queries N+1.
    # --------------------------------------------------

    def _get_carrera(self, obj):
        if not hasattr(obj, '_carrera_cache'):
            all_cc = list(obj.carreras_cursadas.all())
            obj._carrera_cache = all_cc[0] if all_cc else None
        return obj._carrera_cache

    # --------------------------------------------------
    # Campos calculados — legacy (primera carrera)
    # --------------------------------------------------

    def get_carrera_actual(self, obj):
        cc = self._get_carrera(obj)
        return cc.carrera.id_carrera if cc else None

    def get_estado_actual(self, obj):
        cc = self._get_carrera(obj)
        return cc.id_estado.id_estado if cc else None

    def get_carrera_nombre(self, obj):
        cc = self._get_carrera(obj)
        return cc.carrera.descripcion if cc else None

    def get_estado_nombre(self, obj):
        cc = self._get_carrera(obj)
        return cc.id_estado.descripcion if cc else None

    def get_carrera_color(self, obj):
        cc = self._get_carrera(obj)
        return cc.carrera.color if cc else None

    # --------------------------------------------------
    # NUEVO: todas las carreras del alumno
    # --------------------------------------------------

    def get_carreras(self, obj):
        carreras_cursadas = obj.carreras_cursadas.all()

        return [
            {
                "id_carrera":   cc.carrera.id_carrera,
                "descripcion":  cc.carrera.descripcion,
                "color":        cc.carrera.color,
                "estado_id":    cc.id_estado.id_estado,
                "estado":       cc.id_estado.descripcion,
                "anio_ingreso": cc.anio_ingreso,
                "activa":       cc.id_estado.id_estado == 1,
            }
            for cc in carreras_cursadas
        ]

    # --------------------------------------------------
    # Validaciones únicas
    # --------------------------------------------------

    def validate(self, data):
        instance = self.instance

        def check_unique(field):
            value = data.get(field)
            if not value:
                return
            qs = Alumno.objects.filter(**{field: value})
            if instance:
                qs = qs.exclude(id_alumno=instance.id_alumno)
            if qs.exists():
                raise serializers.ValidationError({
                    field: f"Este {field} ya está registrado."
                })

        check_unique("dni")
        check_unique("email")
        check_unique("legajo")

        return data

    # --------------------------------------------------
    # CREATE
    # --------------------------------------------------

    @transaction.atomic
    def create(self, validated_data):
        carrera_id   = validated_data.pop("id_carrera",   None)
        estado_id    = validated_data.pop("id_estado",    1)
        anio_ingreso = validated_data.pop("anio_ingreso", None)

        alumno = Alumno.objects.create(**validated_data)

        if carrera_id:
            CarreraCursada.objects.create(
                alumno_id=alumno.id_alumno,
                carrera_id=carrera_id,
                id_estado_id=estado_id or 1,
                anio_ingreso=anio_ingreso,
            )

        return alumno

    # --------------------------------------------------
    # UPDATE
    # --------------------------------------------------

    @transaction.atomic
    def update(self, instance, validated_data):
        carrera_id = validated_data.pop("id_carrera", None)
        estado_id  = validated_data.pop("id_estado",  None)

        instance = super().update(instance, validated_data)

        carrera_actual = CarreraCursada.objects.filter(
            alumno_id=instance.id_alumno
        ).first()

        if not carrera_actual and carrera_id:
            CarreraCursada.objects.create(
                alumno_id=instance.id_alumno,
                carrera_id=carrera_id,
                id_estado_id=estado_id or 1,
            )
            return instance

        if carrera_actual:
            if estado_id:
                carrera_actual.id_estado_id = estado_id

            if carrera_id and carrera_id != carrera_actual.carrera_id:
                carrera_actual.delete()
                CarreraCursada.objects.create(
                    alumno_id=instance.id_alumno,
                    carrera_id=carrera_id,
                    id_estado_id=estado_id or 1,
                )
            else:
                carrera_actual.save()

        return instance