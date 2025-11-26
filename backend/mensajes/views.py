# En mensajes/views.py

from django.shortcuts import get_object_or_404, render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
# from django.http import JsonResponse
from django.utils import timezone
# from datetime import datetime

from .models import Mensaje
from .serializers import MensajeSerializer
from .mensajes_instantaneos import enviar_mensaje_instantaneo

from alumnos.models import Alumno 
from .enviar_whatsapp import enviar_whatsapp

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
        # 1. Obtener parámetros
        tipo_envio = request.GET.get('tipo_envio', '')
        search = request.GET.get('search', '').strip()  # <--- NUEVO: Capturar búsqueda
        page = int(request.GET.get('page', 1))
        page_size = int(request.GET.get('page_size', 10))

        # 2. Queryset base
        qs = Mensaje.objects.all().order_by('-fecha_creacion')

        # 3. Aplicar filtros
        if tipo_envio:
            qs = qs.filter(tipo_envio=tipo_envio)
        
        if search:  # <--- NUEVO: Lógica de búsqueda
            from django.db.models import Q  # Importar Q al inicio del archivo si no está
            qs = qs.filter(
                Q(titulo__icontains=search) | 
                Q(descripcion__icontains=search)
            )

        # 4. Paginación manual
        total = qs.count()
        start = (page - 1) * page_size
        end = start + page_size
        
        serializer = MensajeSerializer(qs[start:end], many=True)

        return Response({
            'count': total,
            'num_pages': (total + page_size - 1) // page_size,
            'page': page,
            'page_size': page_size,
            'next': end < total, # <--- NUEVO: Flag para saber si hay sig. página
            'results': serializer.data,
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
    
    def post(self, request):
        print("\n--- INICIANDO POST /api/mensajes/ ---")
        
        serializer = MensajeSerializer(data=request.data)
        
        if serializer.is_valid():
            # 1. Guardamos el mensaje primero
            fecha_envio_aware = serializer.validated_data.get('fecha_envio')
            fecha_final = fecha_envio_aware if fecha_envio_aware else timezone.now()

            mensaje = serializer.save(
                fecha_envio=fecha_final,
                estado_envio='pendiente'
            )
            
            # 2. Lógica de envío INSTANTÁNEO (si no es programado)
            if not mensaje.en_programado:
                
                # Obtenemos los IDs de los destinatarios (viene del JSON)
                ids_alumnos = request.data.get('destino_deudores', [])
                
                # --- CASO CORREO ---
                if mensaje.tipo_envio == 'correo':
                    carreras_destino = request.data.get('destino_carrera', [])
                    enviar_mensaje_instantaneo(
                        mensaje,
                        alumnos_destino=ids_alumnos,
                        carreras_destino=carreras_destino
                    )
                    mensaje.estado_envio = 'enviado'
                    mensaje.save()

                # --- CASO WHATSAPP (NUEVO) ---
                elif mensaje.tipo_envio == 'whatsapp':
                    print(f"🚀 Iniciando envío masivo de WhatsApp a {len(ids_alumnos)} alumnos...")
                    
                    # Buscamos los objetos Alumno en la base de datos
                    alumnos = Alumno.objects.filter(pk__in=ids_alumnos)
                    
                    enviados_ok = 0
                    
                    for alumno in alumnos:
                        # IMPORTANTE: Revisa si tu campo se llama 'telefono', 'celular' o 'movil'
                        # Aquí asumo que se llama 'telefono'.
                        telefono = getattr(alumno, 'telefono', None) 
                        
                        if telefono:
                            # Llamamos a nuestra función de utilidad
                            exito = enviar_whatsapp(telefono, mensaje.descripcion)
                            if exito:
                                enviados_ok += 1
                        else:
                            print(f"⚠️ El alumno {alumno.id} no tiene teléfono registrado.")

                    # Actualizamos el estado del mensaje
                    if enviados_ok > 0:
                        mensaje.estado_envio = 'enviado'
                    else:
                        mensaje.estado_envio = 'fallido' # Opcional, si ninguno salió
                        
                    mensaje.save()
                    print(f"🏁 Fin envío WhatsApp. Total enviados: {enviados_ok}")

            return Response(MensajeSerializer(mensaje).data, status=201)
        
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