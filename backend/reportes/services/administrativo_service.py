def get_admin_data():
    data = {
        "kpis": {
            "tramites": 540,
            "modificaciones": 35,
            "bajas": 24,
            "reincorporaciones": 15,
            "mensajes_mes": 120,
            "mensajes_anio": 1450
        },
        "charts": {
            "chartAltasMensuales": {
                "title": {"text": "Altas Mensuales", "textStyle": {"color": "#355CC0"}, "top": "10px", "left": "center"},
                "grid": {"top": "60px", "bottom": "30px", "left": "40px", "right": "20px"},
                "xAxis": {"type": "category", "data": ["Ene", "Feb", "Mar", "Abr", "May", "Jun"]},
                "yAxis": {"type": "value"},
                "series": [
                    {"name": "Altas", "data": [40, 45, 50, 55, 60, 50], "type": "bar"}
                ]
            }
        },
        "tabla_tramites": [
            {"tramite": "Certificados de alumno regular", "cantidad": 180},
            {"tramite": "Reincorporación", "cantidad": 50},
            {"tramite": "Inscripciones", "cantidad": 45}
    ]
    }
    return data