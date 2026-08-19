from django.db import connection


def _fetch_localidad(extra_join="", extra_where="", params=None):
    sql = f"""
        SELECT
            COALESCE(l.nombre, 'Sin información') AS localidad,
            COALESCE(pr.nombre, 'Sin información') AS provincia,
            COUNT(DISTINCT a.id_alumno) AS cantidad
        FROM alumnos_alumno a
        LEFT JOIN geografia_localidad l ON a.ciudad = l.id_loc
        LEFT JOIN geografia_departamento d ON l.departamento_id = d.id_dpto
        LEFT JOIN geografia_provincia pr ON d.provincia_id = pr.id_prov
        {extra_join}
        {('WHERE ' + extra_where) if extra_where else ''}
        GROUP BY l.id_loc, l.nombre, pr.nombre
        ORDER BY cantidad DESC
    """
    with connection.cursor() as c:
        c.execute(sql, params or [])
        cols = [col[0] for col in c.description]
        return [dict(zip(cols, row)) for row in c.fetchall()]


def demografico_data(carrera_id=None, anio=None):
    # Sección 1 — total general por localidad
    general = _fetch_localidad()

    # Sección 2 — por carrera (si se pasó carrera_id)
    por_carrera = []
    carrera_nombre = None
    if carrera_id:
        with connection.cursor() as c:
            c.execute("SELECT descripcion FROM carreras_carrera WHERE id_carrera = %s", [carrera_id])
            row = c.fetchone()
            carrera_nombre = row[0] if row else None

        por_carrera = _fetch_localidad(
            extra_join="JOIN carreras_cursadas cc ON a.id_alumno = cc.alumno_id",
            extra_where="cc.carrera_id = %s",
            params=[carrera_id],
        )

    # Sección 3 — ingresantes (estado_id=5), con filtro opcional de año
    where_ingresantes = "cc2.id_estado_id = 5"
    params_ingresantes = []
    if anio:
        where_ingresantes += " AND cc2.anio_ingreso = %s"
        params_ingresantes.append(anio)

    ingresantes = _fetch_localidad(
        extra_join="JOIN carreras_cursadas cc2 ON a.id_alumno = cc2.alumno_id",
        extra_where=where_ingresantes,
        params=params_ingresantes,
    )

    total_general = sum(r["cantidad"] for r in general)
    for r in general:
        r["pct"] = round(r["cantidad"] * 100 / total_general, 1) if total_general else 0

    return {
        "general": general,
        "por_carrera": por_carrera,
        "carrera_nombre": carrera_nombre,
        "ingresantes": ingresantes,
        "anio": anio,
        "total_general": total_general,
        "total_ingresantes": sum(r["cantidad"] for r in ingresantes),
    }
