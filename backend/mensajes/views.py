from django.shortcuts import get_object_or_404, render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from django.db.models import Q  # Importante para la búsqueda OR

from .models import Mensaje
from .serializers import MensajeSerializer
from .mensajes_instantaneos import enviar_mensaje_instantaneo
from .enviar_whatsapp import enviar_whatsapp
from alumnos.models import Alumno 

# -------------------------------
# Vistas para la plantilla (Frontend)
# -------------------------------
def index(request):
    """
    Renderiza la página principal de mensajes.
    """
    return render(request, 'mensajes/index.html')

# -------------------------------
# Vistas principales de la API
# -------------------------------
class MensajeListCreate(APIView):
    """
    GET: lista todos los mensajes (ordenados por fecha_creacion desc) con búsqueda y paginación.
    POST: crea un nuevo mensaje y envía instantáneamente (Correo o WhatsApp) si no es programado.
    """

    def get(self, request):
        # 1. Obtener parámetros
        tipo_envio = request.GET.get('tipo_envio', '')
        search = request.GET.get('search', '').strip()
        
        # Paginación
        try:
            page = int(request.GET.get('page', 1))
            page_size = int(request.GET.get('page_size', 10))
        except ValueError:
            page = 1
            page_size = 10

        # 2. Queryset base
        qs = Mensaje.objects.all().order_by('-fecha_creacion')

        # 3. Aplicar filtros
        if tipo_envio:
            qs = qs.filter(tipo_envio=tipo_envio)
        
        if search:
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
            'next': end < total,
            'results': serializer.data,
        })

    def post(self, request):
        print("\n--- INICIANDO POST /api/mensajes/ ---")
        
        serializer = MensajeSerializer(data=request.data)
        
        if serializer.is_valid():
            # 1. Determinamos la fecha y guardamos el mensaje en estado 'pendiente'
            fecha_envio_aware = serializer.validated_data.get('fecha_envio')
            fecha_final = fecha_envio_aware if fecha_envio_aware else timezone.now()

            mensaje = serializer.save(
                fecha_envio=fecha_final,
                estado_envio='pendiente'
            )
            
            print(f"Mensaje guardado. ID: {mensaje.id}, Tipo: {mensaje.tipo_envio}")

            # 2. Lógica de envío INSTANTÁNEO (si NO es programado)
            if not mensaje.en_programado:
                
                # Obtenemos listas de destinatarios (vienen del JSON del frontend)
                ids_alumnos = request.data.get('destino_deudores', [])
                ids_carreras = request.data.get('destino_carrera', [])
                
                # --- CASO A: ENVÍO POR CORREO ---
                if mensaje.tipo_envio == 'correo':
                    print("Procesando envío instantáneo de CORREO...")
                    enviar_mensaje_instantaneo(
                        mensaje,
                        alumnos_destino=ids_alumnos,
                        carreras_destino=ids_carreras
                    )
                    # Asumimos éxito tras la llamada a la función de correo
                    mensaje.estado_envio = 'enviado'
                    mensaje.save()

                # --- CASO B: ENVÍO POR WHATSAPP ---
                elif mensaje.tipo_envio == 'whatsapp':
                    print("Procesando envío instantáneo de WHATSAPP...")
                    
                    # Nota: Para WhatsApp necesitamos los números.
                    # Buscamos alumnos directos + alumnos de carreras (si tu lógica lo requiere)
                    # Aquí buscamos solo los seleccionados directamente por ahora:
                    alumnos = Alumno.objects.filter(pk__in=ids_alumnos)
                    
                    enviados_ok = 0
                    
                    for alumno in alumnos:
                        telefono = getattr(alumno, 'telefono', None)
                        if telefono:
                            # Llamamos a tu utilidad de whatsapp
                            exito = enviar_whatsapp(telefono, mensaje.descripcion)
                            if exito:
                                enviados_ok += 1
                        else:
                            print(f"⚠️ Alumno {alumno.nombre} (ID: {alumno.id}) no tiene teléfono.")

                    print(f"🏁 Fin envío WhatsApp. Total enviados: {enviados_ok}")
                    
                    if enviados_ok > 0:
                        mensaje.estado_envio = 'enviado'
                    else:
                        # Si no se envió a nadie, podrías dejarlo pendiente o fallido
                        pass 
                    
                    mensaje.save()

            # Devolvemos el mensaje creado con sus datos actualizados
            return Response(MensajeSerializer(mensaje).data, status=status.HTTP_201_CREATED)
        
        # Si el serializer falla
        print("❌ Error en serializer:", serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MensajeDetail(APIView):
    """
    Maneja operaciones sobre un mensaje específico (GET, PUT, DELETE).
    """
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