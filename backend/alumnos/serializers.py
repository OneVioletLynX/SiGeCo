# backend/alumnos/serializers.py
from rest_framework import serializers
from .models import Alumno
from carreras.models import CarreraCursada

class AlumnoSerializer(serializers.ModelSerializer):
    # Para ALTA / EDICIÓN
    id_carrera = serializers.IntegerField(write_only=True, required=False)
    id_estado = serializers.IntegerField(write_only=True, required=False)

    # Para DETALLE (solo lectura)
    carrera_actual = serializers.SerializerMethodField(read_only=True)
    estado_actual = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Alumno
        fields = '__all__'

    # ------------------------------------------------------------------
    # 🔹 Campos auxiliares de solo lectura
    # ------------------------------------------------------------------
    def get_carrera_actual(self, obj):
        cc = obj.carreras_cursadas.first()
        return cc.carrera.id_carrera if cc else None

    def get_estado_actual(self, obj):
        cc = obj.carreras_cursadas.first()
        return cc.id_estado.id_estado if cc else None

    # ------------------------------------------------------------------
    # 🔹 Crear alumno + carrera cursada
    # ------------------------------------------------------------------
    def create(self, validated_data):
        carrera_id = validated_data.pop('id_carrera', None)
        estado_id = validated_data.pop('id_estado', 1)  # Activo por defecto

        alumno = super().create(validated_data)

        if carrera_id:
            CarreraCursada.objects.create(
                alumno=alumno,
                carrera_id=carrera_id,
                id_estado_id=estado_id
            )
        return alumno

    # ------------------------------------------------------------------
    # 🔹 Actualizar alumno + carrera cursada
    # ------------------------------------------------------------------
# backend/alumnos/serializers.py
from django.db import transaction
from rest_framework import serializers
from .models import Alumno
from carreras.models import CarreraCursada

class AlumnoSerializer(serializers.ModelSerializer):
    # Para ALTA / EDICIÓN (lo envía el form)
    id_carrera = serializers.IntegerField(write_only=True, required=False)
    id_estado = serializers.IntegerField(write_only=True, required=False)

    # Solo lectura (detalle)
    carrera_actual = serializers.SerializerMethodField(read_only=True)
    estado_actual = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Alumno
        fields = '__all__'

    # ---- helpers read-only
    def get_carrera_actual(self, obj):
        cc = obj.carreras_cursadas.first()
        return cc.carrera.id_carrera if cc else None

    def get_estado_actual(self, obj):
        cc = obj.carreras_cursadas.first()
        return cc.id_estado.id_estado if cc else None

    # ---- create
    @transaction.atomic
    def create(self, validated_data):
        carrera_id = validated_data.pop('id_carrera', None)
        estado_id = validated_data.pop('id_estado', 1)  # 1 = Activo por defecto
        alumno = super().create(validated_data)

        if carrera_id:
            # Evitar duplicado si ya existiera por datos “sucios”
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

    # ---- update
    @transaction.atomic
    def update(self, instance, validated_data):
        nueva_carrera_id = validated_data.pop('id_carrera', None)
        nuevo_estado_id  = validated_data.pop('id_estado', None)

        # 1) actualizar campos del Alumno
        instance = super().update(instance, validated_data)

        # 2) sincronizar CarreraCursada evitando duplicados
        actual = instance.carreras_cursadas.first()  # fila actual (si existe)

        # Si no hay fila, crear (pero sin duplicar)
        if not actual:
            if nueva_carrera_id:
                existente = CarreraCursada.objects.filter(
                    alumno_id=instance.id_alumno,
                    carrera_id=nueva_carrera_id
                ).first()
                if existente:
                    # Solo actualizar estado si vino
                    if nuevo_estado_id is not None and existente.id_estado_id != nuevo_estado_id:
                        existente.id_estado_id = nuevo_estado_id
                        existente.save()
                else:
                    CarreraCursada.objects.create(
                        alumno_id=instance.id_alumno,
                        carrera_id=nueva_carrera_id,
                        id_estado_id=nuevo_estado_id or 1
                    )
            # Si tampoco vino carrera, no tocamos nada
            return instance

        # Hay fila actual
        carrera_actual_id = actual.carrera_id
        estado_actual_id  = actual.id_estado_id

        # Caso A: solo cambia estado (misma carrera)
        if (nueva_carrera_id is None) or (nueva_carrera_id == carrera_actual_id):
            if (nuevo_estado_id is not None) and (nuevo_estado_id != estado_actual_id):
                actual.id_estado_id = nuevo_estado_id
                actual.save()
            return instance

        # Caso B: cambió la carrera (¡no modifiques PK!):
        #  - Si ya existe la fila con (alumno, nueva carrera) => actualizá estado allí
        #  - Si no existe => creala
        destino = CarreraCursada.objects.filter(
            alumno_id=instance.id_alumno,
            carrera_id=nueva_carrera_id
        ).first()

        if destino:
            # actualizar estado en destino si vino
            if nuevo_estado_id is not None and destino.id_estado_id != nuevo_estado_id:
                destino.id_estado_id = nuevo_estado_id
                destino.save()
            # borrar la fila vieja para no quedar con dos
            if actual.pk != destino.pk:
                actual.delete()
        else:
            # crear nueva y eliminar la vieja
            CarreraCursada.objects.create(
                alumno_id=instance.id_alumno,
                carrera_id=nueva_carrera_id,
                id_estado_id=(nuevo_estado_id if nuevo_estado_id is not None else estado_actual_id or 1)
            )
            actual.delete()

        return instance

