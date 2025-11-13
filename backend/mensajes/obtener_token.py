# mensajes/obtener_token.py
import os
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ['https://www.googleapis.com/auth/gmail.send']

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    creds_path = os.path.join(script_dir, 'credentials.json')
    token_path = os.path.join(script_dir, 'token.json')

    if not os.path.exists(creds_path):
        print("No encontré credentials.json en:", creds_path)
        return

    flow = InstalledAppFlow.from_client_secrets_file(creds_path, SCOPES)
    creds = flow.run_local_server(port=0)

    with open(token_path, 'w', encoding='utf-8') as f:
        f.write(creds.to_json())

    print("Token guardado en:", token_path)
    print("Listo — ahora podés usar token.json desde gmail_utils.py")

if __name__ == '__main__':
    main()
