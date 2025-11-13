from django.apps import AppConfig
import threading
import time
import logging

logger = logging.getLogger(__name__)

class MensajesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'mensajes'

    def ready(self):
        """
        Inicia un hilo en segundo plano para procesar los mensajes programados
        cada cierto intervalo de tiempo.
        """
        def worker():
            # Importamos aquí para evitar AppRegistryNotReady
            from .mensajes_programados import enviar_mensajes_programados
    
            while True:
                try:
                    logger.info("Worker de mensajes programados: ejecutando check...")
                    enviar_mensajes_programados()
                except Exception as e:
                    logger.error("Error en worker de mensajes programados: %s", e)
                time.sleep(60)  # revisa cada 60 segundos

        thread = threading.Thread(target=worker, daemon=True)
        thread.start()
        logger.info("Worker de mensajes programados iniciado ✅")
