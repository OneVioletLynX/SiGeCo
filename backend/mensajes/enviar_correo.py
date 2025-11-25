# # enviar_correo.py
# import yagmail
# from .config import REMITENTE, APP_PASSWORD

# # Inicializamos yagmail una vez
# yag = yagmail.SMTP(REMITENTE, APP_PASSWORD)

# def enviar_correo(destinatario, asunto, contenido):
#     """
#     Envía un correo a un destinatario con asunto y contenido.
#     """
#     try:
#         yag.send(to=destinatario, subject=asunto, contents=contenido)
#         print(f"Correo enviado ✅ a {destinatario}")
#     except Exception as e:
#         print(f"Error al enviar correo a {destinatario}: {e}")


import yagmail
import time
import logging
from .config import REMITENTE, APP_PASSWORD

logger = logging.getLogger(__name__)

# Inicializamos yagmail una sola vez
yag = yagmail.SMTP(REMITENTE, APP_PASSWORD)

def enviar_correo(destinatario, asunto, contenido, max_retries=2, pause=1):
    """
    Envía un correo a un destinatario con asunto y contenido.
    Devuelve (True, None) si fue exitoso, (False, error) si falla.
    """
    last_error = None
    for attempt in range(1, max_retries + 2):
        try:
            yag.send(to=destinatario, subject=asunto, contents=contenido)
            logger.info("Correo enviado ✅ a %s (intento %s)", destinatario, attempt)
            return True, None
        except Exception as e:
            last_error = e
            logger.exception("Error enviando a %s en intento %s: %s", destinatario, attempt, e)
            time.sleep(pause)  # espera antes de reintentar
    return False, last_error
