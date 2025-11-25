# mensajes_programados.py
import logging
import time
from .enviar_correo import enviar_correo
from .db import (
    obtener_alumnos_activos,
    obtener_mensajes_pendientes,
    marcar_mensaje_enviado,
    marcar_mensaje_error
)

logger = logging.getLogger(__name__)

def enviar_con_reintentos(destinatario, asunto, contenido, max_intentos=3, delay=5):
    """
    Envía un correo con reintentos en caso de fallos temporales.
    """
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
    Envía todos los mensajes pendientes de tipo 'correo' en la base de datos.
    """
    mensajes = obtener_mensajes_pendientes()
    if not mensajes:
        logger.info("No hay mensajes pendientes para enviar.")
        return

    alumnos = obtener_alumnos_activos()

    for mensaje in mensajes:
        titulo = mensaje['titulo'] or "(sin asunto)"
        contenido = mensaje['descripcion'] or ""
        mensaje_id = mensaje['id']

        # Filtramos destinatarios según carrera o lista de alumnos si existe
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
                errores.append({
                    'alumno_id': alumno['id'],
                    'correo': alumno['correo'],
                    'error': str(err)
                })

            # Delay entre correos para evitar timeout con Gmail
            time.sleep(3)

        # Marcar mensaje en DB según resultado
        if not errores:
            marcar_mensaje_enviado(mensaje_id)
            logger.info("Mensaje %s marcado como ENVIADO (%s destinatarios)", mensaje_id, enviados)
        else:
            marcar_mensaje_error(mensaje_id, detalles=errores)
            logger.warning("Mensaje %s marcado con ERRORES: %s", mensaje_id, errores)
