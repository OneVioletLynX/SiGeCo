from rest_framework import serializers
from .models import Mensaje, Alumno, Carrera

class MensajeSerializer(serializers.ModelSerializer):
    # Campos que RECIBEN listas de IDs (solo para escribir)
    destino_deudores = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        allow_empty=True,
        write_only=True
    )
    destino_carrera = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        allow_empty=True,
        write_only=True
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

    # ------------------------------------------------------------------------------------
    # Métodos para mostrar info (ESTA ES LA PARTE CLAVE MODIFICADA)
    # ------------------------------------------------------------------------------------
    def get_destino_deudores_info(self, obj):
        """
        Este método construye la lista final de destinatarios para el Frontend.
        Combina:
        1. Alumnos seleccionados manualmente.
        2. Alumnos que cursan las carreras seleccionadas (solo activos).
        """
        ids_directos = obj.destino_deudores or []
        ids_carreras = obj.destino_carrera or []

        # Empezamos con un QuerySet vacío
        qs = Alumno.objects.none()

        # 1. Sumar alumnos individuales
        if ids_directos:
            qs = qs | Alumno.objects.filter(pk__in=ids_directos)

        # 2. Sumar alumnos de las carreras (Solo ACTIVOS id_estado=1)
        if ids_carreras:
            # Usamos el related_name 'carreras_cursadas' que definimos en el modelo Alumno
            qs_carrera = Alumno.objects.filter(
                carreras_cursadas__carrera_id__in=ids_carreras,
                carreras_cursadas__id_estado_id=1 
            )
            qs = qs | qs_carrera

        # 3. Eliminar duplicados (si un alumno estaba en ambas listas)
        qs = qs.distinct()

        # 4. Devolver los datos necesarios para WhatsApp (Nombre y Teléfono)
        return list(qs.values('id_alumno', 'nombre', 'apellido', 'email', 'telefono'))
    
    def get_destino_carrera_info(self, obj):
        if not obj.destino_carrera:
            return []
        return list(Carrera.objects.filter(id_carrera__in=obj.destino_carrera)
                         .values('id_carrera', 'descripcion'))

    # ------------------------------------------------------------------------------------
    # Crear mensaje
    # ------------------------------------------------------------------------------------
    def create(self, validated_data):
        deudores_ids = validated_data.pop('destino_deudores', [])
        carreras_ids = validated_data.pop('destino_carrera', [])

        mensaje = super().create(validated_data)

        mensaje.destino_deudores = deudores_ids
        mensaje.destino_carrera = carreras_ids
        mensaje.save()

        return mensaje

    # ------------------------------------------------------------------------------------
    # Actualizar mensaje
    # ------------------------------------------------------------------------------------
    def update(self, instance, validated_data):
        deudores_ids = validated_data.pop('destino_deudores', None)
        carreras_ids = validated_data.pop('destino_carrera', None)

        if deudores_ids is not None:
            instance.destino_deudores = deudores_ids
        if carreras_ids is not None:
            instance.destino_carrera = carreras_ids

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance