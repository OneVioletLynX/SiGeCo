# =====================================================
# PERMISOS POR ROL
#
# Para agregar un rol: agregar clave en PERMISOS_POR_ROL.
# Para cambiar accesos: modificar la lista de secciones.
# =====================================================

PERMISOS_POR_ROL = {
    'ADMIN': [
        'cobros', 'alumnos', 'carreras',
        'mensajes', 'reportes', 'estadisticas',
    ],
    'SECRETARIA': [
        'cobros', 'alumnos', 'carreras',
        'mensajes', 'reportes', 'estadisticas',
    ],
    'COORDINADOR': [
        # Sin cobros
        'alumnos', 'carreras',
        'mensajes', 'reportes', 'estadisticas',
    ],
}

# Mapeo endpoint → sección para validar en el backend
ENDPOINT_SECCION = {
    '/ctacte/registrar-pago/': 'cobros',   # ← solo esta ruta de ctacte es cobros
    '/ctacte/pagos/':          'cobros',
    '/ctacte/pendientes/':     'cobros',
    '/api/pago':               'cobros',
    '/api/alumnos':            'alumnos',
    '/api/carreras':           'carreras',
    '/api/mensajes':           'mensajes',
    '/api/seccion':            'reportes',
    '/api/generar_pdf':        'reportes',
}

def tiene_permiso(rol, seccion):
    return seccion in PERMISOS_POR_ROL.get(rol, [])


def get_permisos(rol):
    return PERMISOS_POR_ROL.get(rol, [])


def seccion_desde_path(path):
    """Devuelve la sección correspondiente a un path de la API."""
    for prefijo, seccion in ENDPOINT_SECCION.items():
        if path.startswith(prefijo):
            return seccion
    return None