# mensajes/enviar_whatsapp.py
from twilio.rest import Client
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

def formatear_numero_argentina(telefono):
    """
    Convierte '351 155 123456' -> '+5493515123456'
    Twilio requiere formato E.164 estricto.
    """
    if not telefono:
        return None
    
    # 1. Dejar solo números y el símbolo +
    limpio = "".join(c for c in str(telefono) if c.isdigit() or c == '+')
    
    # 2. Si ya viene con +549 (formato internacional ok), devolverlo
    if limpio.startswith('+549'):
        return limpio

    # 3. Si empieza con 549 (sin el +), agregarlo
    if limpio.startswith('549'):
        return f"+{limpio}"
        
    # 4. Caso común: número local (ej: 3515123456 o 0351...)
    # Quitamos el '0' inicial si existe (ej: 0351 -> 351)
    if limpio.startswith('0'):
        limpio = limpio[1:]
        
    # Quitamos el '15' de celulares si existe y el número es largo
    # (Esto es un heuristic simple, puede requerir ajustes según tu zona)
    # if limpio.startswith('15') and len(limpio) > 8: 
    #    limpio = limpio[2:]

    # Agregamos el prefijo de Argentina (+54) y el 9 de móvil
    return f"+549{limpio}"

def enviar_whatsapp(numero_destino, cuerpo_mensaje):
    """
    Envía el mensaje usando las credenciales de settings.py
    """
    try:
        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        
        # Formatear número
        numero_final = formatear_numero_argentina(numero_destino)
        
        if not numero_final:
            logger.warning(f"Número inválido para WP: {numero_destino}")
            return False

        message = client.messages.create(
            body=cuerpo_mensaje,
            from_=f'whatsapp:{settings.TWILIO_WHATSAPP_NUMBER}',
            to=f'whatsapp:{numero_final}'
        )
        
        print(f"✅ WhatsApp enviado a {numero_final} SID: {message.sid}")
        return True
        
    except Exception as e:
        print(f"❌ Error Twilio enviando a {numero_destino}: {e}")
        return False