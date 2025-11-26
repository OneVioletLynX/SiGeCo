# En mensajes/views.py
from django.shortcuts import get_object_or_404, render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.http import JsonResponse
from django.utils import timezone
from datetime import datetime

from .models import Mensaje
from .serializers import MensajeSerializer
from .mensajes_instantaneos import enviar_mensaje_instantaneo

# -------------------------------
# Vistas principales de la API
# -------------------------------
class MensajeListCreate(APIView):
    """
    GET: lista todos los mensajes (ordenados por fecha_creacion desc)
    POST: crea un nuevo mensaje y envía instantáneamente si corresponde.
    """

    # ----------------------------------------------------
    # MÉTODO GET CORREGIDO (REEMPLAZA TU MÉTODO 'get' ACTUAL)
    # ----------------------------------------------------
    def get(self, request):
        
        # 1. Obtener parámetros de la URL
        tipo_envio = request.GET.get('tipo_envio', '') # El nuevo filtro
        page = int(request.GET.get('page', 1))
        page_size = int(request.GET.get('page_size', 10)) # Default a 10 como en tu JS

        # 2. Queryset base
        qs = Mensaje.objects.all().order_by('-fecha_creacion')

        # 3. Aplicar filtro (si existe)
        if tipo_envio:
            qs = qs.filter(tipo_envio=tipo_envio)

        # 4. Paginación manual (la misma lógica que tenías en 'mensajes_list')
        total = qs.count()
        start = (page - 1) * page_size
        end = start + page_size
        
        # 5. Serializar los resultados de la página
        serializer = MensajeSerializer(qs[start:end], many=True)

        # 6. Devolver respuesta en el formato que el JS espera
        return Response({
            'count': total,
            'num_pages': (total + page_size - 1) // page_size,
            'page': page,
            'page_size': page_size,
            'results': serializer.data, # El JS espera la clave 'results'
        })
    # ----------------------------------------------------
    # FIN DE LA CORRECCIÓN
    # ----------------------------------------------------

    def post(self, request):
        # --- DEBUG: Imprimir datos crudos ---
        print("\n--- INICIANDO POST /api/mensajes/ ---")
        print("DATOS RECIBIDOS (request.data):", request.data)
        # --- FIN DEBUG ---

        serializer = MensajeSerializer(data=request.data)
        
        if serializer.is_valid():
            print("SERIALIZER ES VÁLIDO.")
            
            # --- CORRECCIÓN CLAVE: Usar serializer.save() ---
            
            # 1. Obtenemos la fecha (que ya sabemos que es 'aware' o 'None')
            fecha_envio_aware = serializer.validated_data.get('fecha_envio')
            
            # 2. Determinamos la fecha final
            if fecha_envio_aware:
                fecha_final = fecha_envio_aware
            else:
                fecha_final = timezone.now()

            # 3. Guardamos usando el serializer
            mensaje = serializer.save(
                fecha_envio=fecha_final,
                estado_envio='pendiente' # Estado por defecto
            )
            
            print(f"MENSAJE CREADO CON SERIALIZER.SAVE(). ID: {mensaje.id}, Tipo: {mensaje.tipo_envio}, Programado: {mensaje.en_programado}")

            # --- FIN DE LA CORRECCIÓN ---


            # Envío instantáneo si no es programado
            if mensaje.tipo_envio == 'correo' and not mensaje.en_programado:
                
                print("CONDICIÓN CUMPLIDA: Entrando a bloque de envío instantáneo.")
                
                alumnos_destino = request.data.get('destino_deudores', [])
                carreras_destino = request.data.get('destino_carrera', [])

                print("Alumnos capturados (de request.data) para envío instantáneo:", alumnos_destino)
                print("Carreras capturadas (de request.data) para envío instantáneo:", carreras_destino)

                enviar_mensaje_instantaneo(
                    mensaje,
                    alumnos_destino=alumnos_destino,
                    carreras_destino=carreras_destino
                )
                mensaje.estado_envio = 'enviado'
                mensaje.save() # Guardamos el cambio de estado 'enviado'
                print("Envío (supuestamente) realizado.")
            
            else:
                print("CONDICIÓN NO CUMPLIDA: Omitiendo envío (es programado o no es 'correo').")
            
            # Devolvemos el mensaje serializado (con su ID y estado actualizado)
            return Response(MensajeSerializer(mensaje).data, status=201)
        
        # --- DEBUG: Errores del serializer ---
        print("SERIALIZER NO ES VÁLIDO.")
        print("Errores:", serializer.errors)
        # --- FIN DEBUG ---
        return Response(serializer.errors, status=400)


class MensajeDetail(APIView):
    # ... (Sin cambios aquí) ...
    def get(self, request, pk):
        mensaje = get_object_or_404(Mensaje, pk=pk)
        serializer = MensajeSerializer(mensaje)
        return Response(serializer.data)

    def put(self, request, pk):
        mensaje = get_object_or_404(Mensaje, pk=pk)
        serializer = MensajeSerializer(mensaje, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        mensaje = get_object_or_404(Mensaje, pk=pk)
        mensaje.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# -------------------------------
# Vistas para la plantilla
# -------------------------------
def index(request):
    return render(request, 'mensajes/index.html')


# ----------------------------------------------------
# AHORA PUEDES BORRAR ESTA VISTA 'mensajes_list',
# YA QUE HEMOS MOVIDO SU LÓGICA A 'MensajeListCreate'
# ----------------------------------------------------
# API para la tabla (para fetch en JS)
# def mensajes_list(request):
#     q = request.GET.get('q', '')
# ... (etc)