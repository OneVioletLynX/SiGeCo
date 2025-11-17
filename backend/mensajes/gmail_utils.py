# gmail_utils.py
import os
import base64
from email.mime.text import MIMEText
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Alcance para enviar correos
SCOPES = ['https://www.googleapis.com/auth/gmail.send']

# Archivos de credenciales y token
CREDENTIALS_FILE = os.path.join(os.path.dirname(__file__), 'credentials.json')
TOKEN_FILE = os.path.join(os.path.dirname(__file__), 'token.json')

def obtener_credenciales():
    creds = None
    # Intentar cargar token existente
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    # Si no existe o no es válido, iniciar flujo de autorización
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        # Guardar token para futuras ejecuciones
        with open(TOKEN_FILE, 'w') as token:
            token.write(creds.to_json())
    return creds

def crear_mensaje(destinatario, asunto, cuerpo):
    mensaje = MIMEText(cuerpo, 'plain')
    mensaje['to'] = destinatario
    mensaje['from'] = 'toledoagus421@gmail.com'  # <- tu Gmail
    mensaje['subject'] = asunto
    raw = base64.urlsafe_b64encode(mensaje.as_bytes()).decode()
    return {'raw': raw}

def enviar_correo(destinatario, asunto, cuerpo):
    creds = obtener_credenciales()
    service = build('gmail', 'v1', credentials=creds)
    mensaje = crear_mensaje(destinatario, asunto, cuerpo)
    try:
        service.users().messages().send(userId='me', body=mensaje).execute()
        print(f"✅ Correo enviado a {destinatario}")
    except Exception as e:
        print(f"❌ Error enviando a {destinatario}:", e)

# Ejemplo de uso
if __name__ == "__main__":
    enviar_correo("destinatario@correo.com", "Prueba", "Este es un correo de prueba desde Gmail API")
