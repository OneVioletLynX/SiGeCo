import logging
import time
from django.db.models import Q
from .enviar_correo import enviar_correo

# Importamos el modelo Alumno directamente
from alumnos.models import Alumno

logger = logging.getLogger(__name__)

def enviar_mensaje_instantaneo(mensaje, alumnos_destino=None, carreras_destino=None):
    """
    Envía correo inmediatamente a alumnos seleccionados o de las carreras.
    Usa el ORM de Django para filtrar eficientemente.
    """
    # Aseguramos que sean listas
    ids_alumnos = alumnos_destino or []
    ids_carreras = carreras_destino or []

    # Normalizamos campos del mensaje
    titulo = mensaje.titulo or "(sin asunto)"
    contenido = mensaje.descripcion or ""
    mensaje_id = mensaje.id

    # 1. Construir QuerySet de Destinatarios (Usando ORM de Django)
    destinatarios = Alumno.objects.none()

    # A. Por selección individual
    if ids_alumnos:
        destinatarios = destinatarios | Alumno.objects.filter(id_alumno__in=ids_alumnos)

    # B. Por carrera (Solo alumnos activos en esa carrera)
    if ids_carreras:
        destinatarios = destinatarios | Alumno.objects.filter(
            carreras_cursadas__carrera_id__in=ids_carreras,
            carreras_cursadas__id_estado_id=1 # Filtramos solo activos (ID 1)
        )

    # Eliminar duplicados
    destinatarios = destinatarios.distinct()

    if not destinatarios.exists():
        logger.info(f"⚠️ No se encontraron destinatarios válidos para el mensaje #{mensaje_id}")
        return

    errores = []
    enviados = 0
    total = destinatarios.count()

    logger.info(f"🚀 Iniciando envío instantáneo de mensaje #{mensaje_id} a {total} alumnos.")

    # 2. Iterar y Enviar
    for alumno in destinatarios:
        if not alumno.email:
            logger.warning(f"Alumno {alumno.nombre} (ID: {alumno.id_alumno}) no tiene email.")
            continue

        # Personalización básica
        cuerpo_personalizado = f"Hola {alumno.nombre} {alumno.apellido},\n\n{contenido}"
        
        try:
            # Llamamos a tu función de envío (yagmail)
            enviar_correo(alumno.email, titulo, cuerpo_personalizado)
            enviados += 1
        except Exception as e:
            error_msg = str(e)
            logger.error(f"❌ Error enviando a {alumno.email}: {error_msg}")
            errores.append({'alumno_id': alumno.id_alumno, 'correo': alumno.email, 'error': error_msg})

        # Pequeña pausa para evitar bloqueo de Gmail si son muchos
        time.sleep(1.5)

    # 3. Reporte final en consola/log
    if not errores:
        logger.info(f"✅ Mensaje #{mensaje_id} enviado TOTALMENTE ({enviados}/{total}).")
    else:
        logger.warning(f"⚠️ Mensaje #{mensaje_id} enviado PARCIALMENTE. Enviados: {enviados}. Errores: {len(errores)}")

    # Nota: El estado 'enviado' del mensaje se actualiza en la View que llama a esta función.