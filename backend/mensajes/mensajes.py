# import csv
# from gmail_utils import enviar_correo

# # Limite de Gmail: 500 correos diarios
# MAX_DIARIOS = 500

# def enviar_mensajes_desde_csv(archivo_csv):
#     contador = 0
#     with open(archivo_csv, newline='', encoding='utf-8') as csvfile:
#         reader = csv.DictReader(csvfile)
#         for row in reader:
#             if contador >= MAX_DIARIOS:
#                 print("⚠️ Se alcanzó el límite diario de 500 correos.")
#                 break
#             email = row.get('email')
#             asunto = row.get('asunto')
#             contenido = row.get('contenido')
#             if email and asunto and contenido:
#                 enviar_correo(email, asunto, contenido)
#                 contador += 1
#     print(f"✅ Total de correos enviados hoy: {contador}")

# if __name__ == "__main__":
#     enviar_mensajes_desde_csv('mails.csv')
