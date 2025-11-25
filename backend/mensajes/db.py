# db.py
import pymysql
import json
from .config import DB_HOST, DB_USER, DB_PASSWORD, DB_NAME, DB_PORT
from .models import Mensaje
from django.utils import timezone


def get_db_connection():
    """
    Conexión a la base de datos MySQL
    """
    return pymysql.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        db=DB_NAME,
        port=DB_PORT,
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor
    )

def obtener_alumnos_activos():
    """
    Devuelve todos los alumnos activos
    """
    conexion = get_db_connection()
    cursor = conexion.cursor()
    cursor.execute("""
        SELECT 
            id_alumno AS id, 
            nombre, 
            apellido, 
            email AS correo, 
            anio_ingreso AS carrera
        FROM alumnos_alumno
    """)
    alumnos = cursor.fetchall()
    conexion.close()
    return alumnos

def marcar_mensaje_enviado(id_mensaje):
    """
    Marca un mensaje como enviado
    """
    conexion = get_db_connection()
    cursor = conexion.cursor()
    cursor.execute(
        "UPDATE mensajes SET estado_envio='enviado', fecha_envio=NOW() WHERE id=%s",
        (id_mensaje,)
    )
    conexion.commit()
    conexion.close()

def marcar_mensaje_error(id_mensaje, detalles=None):
    """
    Marca un mensaje como con error y guarda los detalles en el campo 'errores'
    """
    conexion = get_db_connection()
    cursor = conexion.cursor()
    detalles_str = json.dumps(detalles, ensure_ascii=False) if detalles else None
    cursor.execute(
        "UPDATE mensajes SET estado_envio='error', errores=%s WHERE id=%s",
        (detalles_str, id_mensaje)
    )
    conexion.commit()
    conexion.close()


def obtener_mensajes_pendientes():
    now = timezone.now()
    return Mensaje.objects.filter(
        tipo_envio='correo',
        en_programado=True,
        estado_envio='pendiente',
        fecha_envio__lte=now
    ).values()