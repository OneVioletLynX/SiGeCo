import os
import threading
import time
import logging
from django.apps import AppConfig

logger = logging.getLogger(__name__)

class MensajesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'mensajes'

    def ready(self):
        """
        Este método se ejecuta cuando Django arranca.
        Iniciamos aquí el hilo en segundo plano para los correos programados.
        """
        
        # EVITAR DUPLICADOS:
        # runserver inicia dos procesos (uno para vigilar cambios y otro para el servidor).
        # Solo queremos correr el hilo en el proceso principal del servidor ('RUN_MAIN' == 'true').
        if os.environ.get('RUN_MAIN') == 'true':
            self.start_background_worker()

    def start_background_worker(self):
        # Definimos la tarea repetitiva
        def worker():
            # Importamos aquí dentro para evitar errores de "Apps no cargadas"
            from .mensajes_programados import procesar_mensajes_programados
            
            logger.info("🤖 Robot de mensajería iniciado en segundo plano.")
            
            while True:
                try:
                    # Ejecutar la lógica de envío
                    procesar_mensajes_programados()
                except Exception as e:
                    logger.error(f"❌ Error en el robot de mensajería: {e}")
                
                # Esperar 60 segundos antes de la próxima revisión
                time.sleep(60)

        # Crear y arrancar el hilo en modo 'daemon' (muere si cierras el servidor)
        hilo = threading.Thread(target=worker, daemon=True)
        hilo.start()