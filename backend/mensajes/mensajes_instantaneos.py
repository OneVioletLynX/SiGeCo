from .enviar_correo import enviar_correo
from .db import obtener_alumnos_activos, marcar_mensaje_enviado, marcar_mensaje_error
import logging

logger = logging.getLogger(__name__)

def enviar_mensaje_instantaneo(mensaje, alumnos_destino=None, carreras_destino=None):
    """
    Envía correo inmediatamente a alumnos seleccionados o de las carreras.
    """
    alumnos_destino = alumnos_destino or []
    carreras_destino = carreras_destino or []

    alumnos = obtener_alumnos_activos()

    # Normalizamos campos del mensaje
    titulo = getattr(mensaje, 'titulo', "(sin asunto)")
    contenido = getattr(mensaje, 'descripcion', "")
    mensaje_id = getattr(mensaje, 'id')


    if not titulo:
        titulo = "(sin asunto)"
    if not contenido:
        contenido = ""

    # Filtramos destinatarios según selección
    destinatarios = [
        a for a in alumnos 
        if (not alumnos_destino and not carreras_destino) or a['id'] in alumnos_destino or a['carrera'] in carreras_destino
    ]

    if not destinatarios:
        logger.info("No se encontraron destinatarios para el mensaje %s", mensaje_id)
        return

    errores = []
    enviados = 0

    for alumno in destinatarios:
        cuerpo = f"Hola {alumno['nombre']} {alumno['apellido']},\n\n{contenido}"
        ok, err = enviar_correo(alumno['correo'], titulo, cuerpo)
        if ok:
            enviados += 1
        else:
            errores.append({'alumno_id': alumno['id'], 'correo': alumno['correo'], 'error': str(err)})

    # Marcar mensaje en DB según resultado
    if not errores:
        marcar_mensaje_enviado(mensaje_id)
        logger.info("Mensaje %s marcado como ENVIADO (%s destinatarios)", mensaje_id, enviados)
    else:
        marcar_mensaje_error(mensaje_id, detalles=errores)
        logger.warning("Mensaje %s marcado con ERRORES: %s", mensaje_id, errores)
