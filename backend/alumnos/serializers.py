# backend/alumnos/serializers.py
from django.db import transaction
from rest_framework import serializers
from .models import Alumno
from carreras.models import CarreraCursada


class AlumnoSerializer(serializers.ModelSerializer):
    # Para ALTA / EDICIÓN (lo envía el form)
    id_carrera = serializers.IntegerField(write_only=True, required=False)
    id_estado = serializers.IntegerField(write_only=True, required=False)

    # Solo lectura (para listar / detalle)
    carrera_actual = serializers.SerializerMethodField(read_only=True)   # id de carrera
    estado_actual = serializers.SerializerMethodField(read_only=True)    # id de estado

    carrera_nombre = serializers.SerializerMethodField(read_only=True)   # texto carrera
    estado_nombre = serializers.SerializerMethodField(read_only=True)    # texto estado

    class Meta:
        model = Alumno
        fields = [
            # ----- Campos reales del modelo Alumno -----
            'id_alumno',
            'legajo',
            'nombre',
            'apellido',
            'fecha_nacimiento',
            'dni',
            'ciudad',
            'direccion',
            'numero',
            'prefijo',
            'telefono',
            'email',
            'inscripcion',
            'fecha_inscripcion',
            'anio_ingreso',

            # ----- Campos WRITE-ONLY para manejo de carrera/estado -----
            'id_carrera',
            'id_estado',

            # ----- Campos READ-ONLY -----
            'carrera_actual',
            'estado_actual',
            'carrera_nombre',
            'estado_nombre',
        ]

    # ------------------------------------------------------------------
    # Helpers de solo lectura
    # ------------------------------------------------------------------
    def _get_carrera_cursada(self, obj):
        # Por ahora tomamos la PRIMERA carrera cursada
        return obj.carreras_cursadas.select_related('carrera', 'id_estado').first()

    def get_carrera_actual(self, obj):
        cc = self._get_carrera_cursada(obj)
        return cc.carrera.id_carrera if cc and cc.carrera else None

    def get_estado_actual(self, obj):
        cc = self._get_carrera_cursada(obj)
        return cc.id_estado.id_estado if cc and cc.id_estado else None

    def get_carrera_nombre(self, obj):
        cc = self._get_carrera_cursada(obj)
        return cc.carrera.descripcion if cc and cc.carrera else None

    def get_estado_nombre(self, obj):
        cc = self._get_carrera_cursada(obj)
        return cc.id_estado.descripcion if cc and cc.id_estado else None


        # ------------------------------------------------------------------
    # VALIDACIONES DE UNICIDAD (DNI, EMAIL, LEGAJO)
    # ------------------------------------------------------------------
    def validate(self, data):
        instance = self.instance  # None si es POST, objeto si es PUT

        dni = data.get('dni')
        email = data.get('email')
        legajo = data.get('legajo')

        # ----- DNI único -----
        if dni is not None:
            qs = Alumno.objects.filter(dni=dni)
            if instance:
                qs = qs.exclude(id_alumno=instance.id_alumno)
            if qs.exists():
                raise serializers.ValidationError({
                    "dni": "Este DNI ya está registrado."
                })

        # ----- EMAIL único -----
        if email:
            qs = Alumno.objects.filter(email=email)
            if instance:
                qs = qs.exclude(id_alumno=instance.id_alumno)
            if qs.exists():
                raise serializers.ValidationError({
                    "email": "Este email ya está registrado."
                })

        # ----- LEGAJO único (si no es null) -----
        if legajo:
            qs = Alumno.objects.filter(legajo=legajo)
            if instance:
                qs = qs.exclude(id_alumno=instance.id_alumno)
            if qs.exists():
                raise serializers.ValidationError({
                    "legajo": "Este legajo ya está registrado."
                })

        return data


    # ------------------------------------------------------------------
    # create
    # ------------------------------------------------------------------
    @transaction.atomic
    def create(self, validated_data):
        carrera_id = validated_data.pop('id_carrera', None)
        estado_id = validated_data.pop('id_estado', 1)  # 1 = Activo por defecto
        alumno = super().create(validated_data)

        if carrera_id:
            existente = CarreraCursada.objects.filter(
                alumno_id=alumno.id_alumno,
                carrera_id=carrera_id
            ).first()
            if existente:
                if existente.id_estado_id != estado_id:
                    existente.id_estado_id = estado_id
                    existente.save()
            else:
                CarreraCursada.objects.create(
                    alumno_id=alumno.id_alumno,
                    carrera_id=carrera_id,
                    id_estado_id=estado_id
                )

        return alumno

    # ------------------------------------------------------------------
    # update
    # ------------------------------------------------------------------
    @transaction.atomic
    def update(self, instance, validated_data):
        nueva_carrera_id = validated_data.pop('id_carrera', None)
        nuevo_estado_id = validated_data.pop('id_estado', None)

        # Primero actualizamos los campos del alumno
        instance = super().update(instance, validated_data)

        actual = CarreraCursada.objects.filter(alumno_id=instance.id_alumno).first()

        # Si no hay fila actual y vino carrera, la creamos
        if not actual:
            if nueva_carrera_id:
                CarreraCursada.objects.create(
                    alumno_id=instance.id_alumno,
                    carrera_id=nueva_carrera_id,
                    id_estado_id=nuevo_estado_id or 1
                )
            return instance

        # Hay fila actual
        carrera_actual_id = actual.carrera_id
        estado_actual_id = actual.id_estado_id

        # Caso 1: solo quiero cambiar estado
        if not nueva_carrera_id and nuevo_estado_id is not None:
            actual.id_estado_id = nuevo_estado_id
            actual.save()
            return instance

        # Caso 2: solo quiero cambiar carrera (opcionalmente estado)
        if nueva_carrera_id and nueva_carrera_id == carrera_actual_id:
            # Misma carrera, solo update de estado
            if nuevo_estado_id is not None and nuevo_estado_id != estado_actual_id:
                actual.id_estado_id = nuevo_estado_id
                actual.save()
            return instance

        # Caso 3: cambiar carrera (y opcionalmente estado)
        if nueva_carrera_id and nueva_carrera_id != carrera_actual_id:
            destino = CarreraCursada.objects.filter(
                alumno_id=instance.id_alumno,
                carrera_id=nueva_carrera_id
            ).first()

            if destino:
                if nuevo_estado_id is not None:
                    if destino.id_estado_id != nuevo_estado_id:
                        destino.id_estado_id = nuevo_estado_id
                        destino.save()
            else:
                CarreraCursada.objects.create(
                    alumno_id=instance.id_alumno,
                    carrera_id=nueva_carrera_id,
                    id_estado_id=(nuevo_estado_id if nuevo_estado_id is not None else estado_actual_id or 1)
                )
            # si querés mantener solo una fila por alumno, podés borrar la anterior:
            if actual.pk != destino.pk if 'destino' in locals() and destino else True:
                actual.delete()

        return instance
