from alumnos.models import Alumno
from carreras.models import CarreraCursada, Carrera, Estado
from django.db.models import Q

def alumnos_filter_data(filters=None):
    if filters is None:
        filters = {}
        
    estado_ids = filters.get('estado')
    carrera_id = filters.get('carrera')

    if isinstance(estado_ids, str):
        estado_ids = [estado_ids]
    elif estado_ids is None:
        estado_ids = []
        
    alumnos_query = Alumno.objects.all()
    if estado_ids:
        alumnos_query = alumnos_query.filter(
            carreras_cursadas__id_estado__id_estado__in=estado_ids
        )
        
    # 🔹 Filtro por Carrera
    if carrera_id and carrera_id != "all":
        alumnos_query = alumnos_query.filter(
            carreras_cursadas__carrera__id_carrera=carrera_id
        )
    alumnos_data = alumnos_query.select_related().values(
        'legajo', 'apellido', 'nombre', 'dni', 'direccion', 'numero', 'prefijo', 'telefono', 'email',
        'carreras_cursadas__carrera__id_carrera',
        'carreras_cursadas__carrera__descripcion',
        'carreras_cursadas__id_estado__id_estado',
        'carreras_cursadas__id_estado__descripcion'
    ).distinct()

    report_list = []
    for data in alumnos_data:
        report_list.append({
            'legajo': data['legajo'],
            'apellido': data['apellido'],
            'nombre': data['nombre'],
            'dni': data['dni'],
            'direccion': f"{data['direccion']} {data['numero']}",
            'telefono': f"{data['prefijo']}-{data['telefono']}",
            'email': data['email'],
            'carrera_id': data['carreras_cursadas__carrera__id_carrera'],
            'carrera': data['carreras_cursadas__carrera__descripcion'],
            'estado_id': data['carreras_cursadas__id_estado__id_estado'],
            'estado': data['carreras_cursadas__id_estado__descripcion'],
        })
        
    return report_list