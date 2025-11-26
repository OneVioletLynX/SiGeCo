# mensajes/enviar_whatsapp.py
from twilio.rest import Client
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

def formatear_numero_argentina(prefijo, telefono):
    """
    Combina prefijo + teléfono y devuelve formato E.164 para WhatsApp:
    +549{prefijo}{telefono}

    Reglas Argentina:
    - eliminar 0 del prefijo si existe (0351 → 351)
    - eliminar el 15 si el número lo incluye (15551234 → 5551234)
    - agregar +54 9 al inicio
    """

    if not prefijo or not telefono:
        return None

    prefijo = str(prefijo).strip()
    telefono = str(telefono).strip()

    # Sacar 0 inicial del prefijo
    if prefijo.startswith("0"):
        prefijo = prefijo[1:]

    # Sacar el 15 del teléfono si lo tiene
    if telefono.startswith("15") and len(telefono) > 8:
        telefono = telefono[2:]

    # Número final para Twilio
    return f"+549{prefijo}{telefono}"


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