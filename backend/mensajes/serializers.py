from rest_framework import serializers
from .models import Mensaje, Alumno, Carrera

class MensajeSerializer(serializers.ModelSerializer):
    # Campos que RECIBEN listas de IDs (solo para escribir)
    destino_deudores = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        allow_empty=True,
        write_only=True  # write_only=True es clave aquí
    )
    destino_carrera = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        allow_empty=True,
        write_only=True  # write_only=True es clave aquí
    )

    # Campos que MUESTRAN info (solo para leer)
    destino_deudores_info = serializers.SerializerMethodField()
    destino_carrera_info = serializers.SerializerMethodField()

    # Fechas
    fecha_envio = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, allow_null=True)
    fecha_creacion = serializers.DateTimeField(read_only=True)
    fecha_modificacion = serializers.DateTimeField(read_only=True)

    class Meta:
        model = Mensaje
        fields = [
            'id',
            'titulo', 'descripcion', 'fecha_envio', 'tipo_envio',
            'en_programado', 'estado_envio',
            
            # Campos de escritura (los ListField)
            'destino_deudores', 'destino_carrera', 
            
            # Campos de lectura (los _info)
            'destino_deudores_info', 'destino_carrera_info', 
            
            'fecha_creacion', 'fecha_modificacion'
        ]
        read_only_fields = [
            'id',
            'fecha_creacion', 'fecha_modificacion',
            'destino_deudores_info', 'destino_carrera_info',
            'estado_envio'
        ]

    # ---------------------------
    # Métodos para mostrar info
    # ---------------------------
    def get_destino_deudores_info(self, obj):
        # 'obj' es la instancia de Mensaje
        # obj.destino_deudores es el campo JSONField (una lista de IDs)
        if not obj.destino_deudores:
            return []
        return list(Alumno.objects.filter(id_alumno__in=obj.destino_deudores)
                       .values('id_alumno', 'nombre', 'apellido', 'email'))

    def get_destino_carrera_info(self, obj):
        # obj.destino_carrera es el campo JSONField (una lista de IDs)
        if not obj.destino_carrera:
            return []
        return list(Carrera.objects.filter(id_carrera__in=obj.destino_carrera)
                       .values('id_carrera', 'descripcion'))

    # ---------------------------
    # Crear mensaje (ESTA ES LA CORRECCIÓN)
    # ---------------------------
    def create(self, validated_data):
        # 1. Sacamos las listas de los datos validados
        deudores_ids = validated_data.pop('destino_deudores', [])
        carreras_ids = validated_data.pop('destino_carrera', [])

        # 2. Creamos el objeto Mensaje con el RESTO de los datos
        #    (validated_data ya no tiene las listas 'virtuales')
        mensaje = super().create(validated_data)

        # 3. Asignamos manualmente las listas a los campos JSONField del modelo
        mensaje.destino_deudores = deudores_ids
        mensaje.destino_carrera = carreras_ids
        
        # 4. Guardamos el objeto Mensaje con las listas ya asignadas
        mensaje.save()

        return mensaje

    # ---------------------------
    # Actualizar mensaje (Corregido también por si acaso)
    # ---------------------------
    def update(self, instance, validated_data):
        # Sacamos las listas
        deudores_ids = validated_data.pop('destino_deudores', None)
        carreras_ids = validated_data.pop('destino_carrera', None)

        # Asignamos las listas si es que vinieron
        if deudores_ids is not None:
            instance.destino_deudores = deudores_ids
        if carreras_ids is not None:
            instance.destino_carrera = carreras_ids

        # Actualizamos el resto de los campos
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance