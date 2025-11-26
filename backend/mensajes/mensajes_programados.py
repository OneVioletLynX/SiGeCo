import os
import sys
import time
import logging
import django
from django.utils import timezone
from django.db import transaction

# Configuracion del entorno para ejecucion standalone (Cron/Task Scheduler)
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

# Importacion de modelos (debe ocurrir despues de django.setup)
from mensajes.models import Mensaje
from alumnos.models import Alumno
from mensajes.enviar_correo import enviar_correo

# Configuracion de Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [%(levelname)s] - %(message)s',
    handlers=[
        logging.FileHandler("logs_envios.log", encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def enviar_con_reintentos(destinatario, asunto, contenido, max_intentos=3):
    """
    Intenta enviar correo usando yagmail con mecanismo de reintento.
    """
    for intento in range(1, max_intentos + 1):
        try:
            enviar_correo(destinatario, asunto, contenido)
            return True, None
        except Exception as e:
            logger.warning(f"Fallo intento {intento} para {destinatario}: {e}")
            time.sleep(2)
    
    return False, f"Fallo tras {max_intentos} intentos."

def procesar_mensajes_programados():
    """
    Proceso principal:
    1. Busca mensajes pendientes tipo 'correo' con fecha vencida.
    2. Resuelve la lista de destinatarios (por ID o por Carrera).
    3. Ejecuta el envio masivo secuencial.
    """
    ahora = timezone.now()
    logger.info("Iniciando revision de mensajes programados...")

    # Filtro: Pendientes + Programados + Correo + Fecha vencida
    mensajes = Mensaje.objects.filter(
        estado_envio='pendiente',
        en_programado=True,
        tipo_envio='correo',
        fecha_envio__lte=ahora
    )

    if not mensajes.exists():
        logger.info("No hay mensajes pendientes para procesar.")
        return

    logger.info(f"Mensajes encontrados: {mensajes.count()}")

    for mensaje in mensajes:
        try:
            logger.info(f"Procesando Mensaje ID {mensaje.id}: '{mensaje.titulo}'")
            
            # Recuperar listas de destinatarios del JSONField
            ids_deudores = mensaje.destino_deudores or []
            ids_carreras = mensaje.destino_carrera or []
            
            destinatarios = Alumno.objects.none()

            # 1. Agregar alumnos por seleccion individual
            if ids_deudores:
                destinatarios = destinatarios | Alumno.objects.filter(id_alumno__in=ids_deudores)
            
            # 2. Agregar alumnos por carrera (Solo estado Activo ID=1)
            if ids_carreras:
                destinatarios = destinatarios | Alumno.objects.filter(
                    carreras_cursadas__carrera_id__in=ids_carreras,
                    carreras_cursadas__id_estado_id=1
                )
            
            # Eliminar duplicados del QuerySet
            destinatarios = destinatarios.distinct()
            
            total_dest = destinatarios.count()
            if total_dest == 0:
                logger.warning(f"Mensaje ID {mensaje.id} sin destinatarios validos. Marcando como enviado.")
                mensaje.estado_envio = 'enviado'
                mensaje.save()
                continue

            enviados_ok = 0
            errores_log = []

            # Ciclo de envio
            for alumno in destinatarios:
                if not alumno.email:
                    errores_log.append(f"ID {alumno.id_alumno}: Sin email registrado")
                    continue

                cuerpo_personalizado = f"Hola {alumno.nombre},\n\n{mensaje.descripcion}"
                
                exito, error = enviar_con_reintentos(alumno.email, mensaje.titulo, cuerpo_personalizado)
                
                if exito:
                    enviados_ok += 1
                else:
                    errores_log.append(f"{alumno.email}: {error}")
                
                # Delay para evitar bloqueo de SMTP (rate limit)
                time.sleep(3)

            # Actualizacion de estado final
            mensaje.estado_envio = 'enviado'
            mensaje.fecha_modificacion = timezone.now()
            mensaje.save()

            logger.info(f"Mensaje ID {mensaje.id} finalizado. Enviados: {enviados_ok}/{total_dest}.")
            
            if errores_log:
                logger.error(f"Errores en Mensaje ID {mensaje.id}: {errores_log}")

        except Exception as e:
            logger.error(f"Error critico en Mensaje ID {mensaje.id}: {e}")

if __name__ == "__main__":
    procesar_mensajes_programados()