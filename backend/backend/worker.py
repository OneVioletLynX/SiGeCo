import logging
import time
from datetime import datetime, timezone
from .enviar_correo import enviar_correo
from .db import (
    obtener_alumnos_activos,
    obtener_mensajes_pendientes,
    marcar_mensaje_enviado,
    marcar_mensaje_error
)

logger = logging.getLogger(__name__)

def enviar_con_reintentos(destinatario, asunto, contenido, max_intentos=3, delay=5):
    for intento in range(1, max_intentos + 1):
        try:
            enviar_correo(destinatario, asunto, contenido)
            return True, None
        except Exception as e:
            logger.warning("Error enviando a %s en intento %d: %s", destinatario, intento, e)
            time.sleep(delay)
    return False, f"No se pudo enviar después de {max_intentos} intentos."

def enviar_mensajes_programados():
    """
    Envía todos los mensajes pendientes de tipo 'correo' cuya fecha_envio
    ya haya llegado o pasado.
    """
    mensajes = obtener_mensajes_pendientes()
    if not mensajes:
        logger.info("No hay mensajes pendientes para enviar.")
        return

    ahora = datetime.now(timezone.utc)  # Hora actual con timezone

    alumnos = obtener_alumnos_activos()

    for mensaje in mensajes:
        fecha_envio = mensaje['fecha_envio']
        if not fecha_envio:
            # Si no tiene fecha, ignoramos o podés enviar ya
            continue

        if fecha_envio > ahora:
            # Todavía no es hora de enviar
            continue

        titulo = mensaje['titulo'] or "(sin asunto)"
        contenido = mensaje['descripcion'] or ""
        mensaje_id = mensaje['id']

        destino_carreras = mensaje.get('destino_carrera', []) or []
        destino_deudores = mensaje.get('destino_deudores', []) or []

        destinatarios = [
            a for a in alumnos
            if (not destino_carreras and not destino_deudores)
            or a['id'] in destino_deudores
            or a.get('carrera') in destino_carreras
        ]

        if not destinatarios:
            logger.info("No se encontraron destinatarios para el mensaje %s", mensaje_id)
            continue

        errores = []
        enviados = 0

        for alumno in destinatarios:
            cuerpo = f"Hola {alumno['nombre']} {alumno['apellido']},\n\n{contenido}"
            ok, err = enviar_con_reintentos(alumno['correo'], titulo, cuerpo)
            if ok:
                enviados += 1
            else:
                errores.append({'alumno_id': alumno['id'], 'correo': alumno['correo'], 'error': str(err)})

            time.sleep(3)

        if not errores:
            marcar_mensaje_enviado(mensaje_id)
            logger.info("Mensaje %s marcado como ENVIADO (%s destinatarios)", mensaje_id, enviados)
        else:
            marcar_mensaje_error(mensaje_id, detalles=errores)
            logger.warning("Mensaje %s marcado con ERRORES: %s", mensaje_id, errores)
