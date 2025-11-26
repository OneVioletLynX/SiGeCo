# backend/alumnos/serializers.py

from django.db import transaction
from rest_framework import serializers
from .models import Alumno
from carreras.models import CarreraCursada
# Si tienes un Serializer para Carrera y Estado, impórtalo aquí.
# from carreras.serializers import CarreraSerializer, EstadoSerializer 

class AlumnoSerializer(serializers.ModelSerializer):
    # ------------------------------------------------------------------
    # 🔹 Campos de ALTA/EDICIÓN (Write Only)
    # ------------------------------------------------------------------
    id_carrera = serializers.IntegerField(write_only=True, required=False)
    id_estado = serializers.IntegerField(write_only=True, required=False)

    # ------------------------------------------------------------------
    # 🔹 Campos de DETALLE (Read Only - Lo que usa el front)
    # ------------------------------------------------------------------
    carrera_actual = serializers.SerializerMethodField(read_only=True)
    estado_actual = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Alumno
        # LISTA EXPLÍCITA: Es vital incluir los campos de teléfono que el frontend necesita.
        fields = [
            'id_alumno', 'legajo', 'nombre', 'apellido', 'dni', 
            'fecha_nacimiento', 'ciudad', 'direccion', 'email',
            'telefono',            # <--- AÑADIDO: Campo para el WhatsApp
            'inscripcion', 'fecha_inscripcion', 'anio_ingreso',
            'carrera_actual', 'estado_actual',
            'id_carrera', 'id_estado', # Write-only fields
        ]

    # ------------------------------------------------------------------
    # 🔹 Implementaciones de SerializerMethodField
    # ------------------------------------------------------------------
    def get_carrera_actual(self, obj):
        cc = obj.carreras_cursadas.first()
        return cc.carrera.id_carrera if cc and cc.carrera else None

    def get_estado_actual(self, obj):
        cc = obj.carreras_cursadas.first()
        return cc.id_estado.id_estado if cc and cc.id_estado else None

    # ------------------------------------------------------------------
    # 🔹 Operaciones: Create y Update (Con lógica transaccional CarreraCursada)
    # ------------------------------------------------------------------
    @transaction.atomic
    def create(self, validated_data):
        carrera_id = validated_data.pop('id_carrera', None)
        estado_id = validated_data.pop('id_estado', 1) 
        
        alumno = super().create(validated_data)

        if carrera_id:
            # Sincronización de CarreraCursada (asegurando atomicidad)
            CarreraCursada.objects.create(
                alumno=alumno,
                carrera_id=carrera_id,
                id_estado_id=estado_id
            )
        return alumno

    @transaction.atomic
    def update(self, instance, validated_data):
        nueva_carrera_id = validated_data.pop('id_carrera', None)
        nuevo_estado_id  = validated_data.pop('id_estado', None)

        # 1) Actualizar campos directos del Alumno
        instance = super().update(instance, validated_data)

        # 2) Lógica compleja de sincronización de CarreraCursada
        actual = instance.carreras_cursadas.first()

        if nueva_carrera_id is not None:
            # Si vino un ID de carrera, buscamos o creamos la CarreraCursada para ese par (alumno, carrera)
            destino, creado = CarreraCursada.objects.get_or_create(
                alumno_id=instance.id_alumno,
                carrera_id=nueva_carrera_id,
                defaults={'id_estado_id': nuevo_estado_id or 1}
            )

            if not creado and nuevo_estado_id is not None:
                # Si existía, solo actualizamos el estado si es necesario
                if destino.id_estado_id != nuevo_estado_id:
                    destino.id_estado_id = nuevo_estado_id
                    destino.save()
            
            # Borrar la fila vieja si existía y es diferente a la que actualizamos/creamos
            if actual and actual.pk != destino.pk:
                actual.delete()

        # Si solo vino el estado (sin cambiar carrera), lo actualizamos en la fila actual
        elif actual and nuevo_estado_id is not None and nuevo_estado_id != actual.id_estado_id:
            actual.id_estado_id = nuevo_estado_id
            actual.save()

        # Si no había fila y no vino carrera, no hacemos nada (el alumno no cursa nada)
        # Si no había fila y vino carrera, ya lo maneja get_or_create/create.

        return instance