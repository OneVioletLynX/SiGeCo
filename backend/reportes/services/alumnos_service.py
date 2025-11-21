from reportes.repositories.alumnos_repo import get_kpis_alumnos, get_charts_alumnos


def get_alumnos_data():
    # 1. Obtener los datos del repositorio
    data_kpis = get_kpis_alumnos()
    kpis = data_kpis["kpis"]
    data_charts_repo = get_charts_alumnos()
    charts_data = data_charts_repo["charts_data"]

    data = {
        "kpis": kpis,
        "charts": {
            # --- Egresados vs Ingresantes ---
            "chartEgreIngre": {
                "title": {"text": "Egresados vs Ingresantes", "textStyle": {"color": "#355CC0"}, "top": "10px", "left": "center"},
                "legend": {"data": ["Egresados", "Ingresantes"], "textStyle": {"color": "#355CC0"}, "bottom": "10px"},
                "xAxis": {"type": "category", "data": charts_data["years"]},  
                "yAxis": {"type": "value"},
                "grid": {"top": 60, "right": 20, "bottom": 50, "left": 50},
                "series": [
                    {"name": "Egresados", "data": charts_data["egresados"], "type": "bar"},  
                    {"name": "Ingresantes", "data": charts_data["ingresantes"], "type": "bar"},  
                ]
            },
            # --- Distribución por Carrera ---
            "chartPorCarrera": {
                "title": {"text": "Distribución por Carrera", "textStyle": {"color": "#355CC0"}, "top": "10px", "left": "center"},
                "tooltip": {"trigger": "item"},
                "series": [{
                    "type": "pie",
                    "radius": "40%",
                    "data": charts_data["por_carrera"]  
                }]
            },
            # --- Distribución por Género ---
            "chartGenero": {
                "title": {"text": "Distribución por género", "textStyle": {"color": "#355CC0"}, "top": "10px", "left": "center"},
                "tooltip": {"trigger": "item"},
                "series": [{
                    "type": "pie",
                    "radius": "60%",
                    "data": charts_data["por_genero"]  
                }]
            },
            # --- Distribución por Edad ---
            "chartEdad": {
                "title": {"text": "Distribución por edad", "textStyle": {"color": "#355CC0"}, "top": "10px", "left": "center"},
                "grid": {"top": 60, "right": 20, "bottom": 50, "left": 50},
                "xAxis": {"type": "category", "data": ["18-22", "23-27", "28-32", "33+"]},
                "yAxis": {"type": "value"},
                "series": [{"data": charts_data["por_edad"], "type": "bar"}] 
            },
            # --- Distribución Geográfica ---
            "chartGeografia": {
                "title": {"text": "Distribución geográfica", "textStyle": {"color": "#355CC0"}, "top": "10px", "left": "center"},
                "tooltip": {"trigger": "item"},
                "grid": {"top": 80, "right": 20, "bottom": 20, "left": 50},
                "series": [{
                    "type": "pie",
                    "radius": "50%",
                    "data": charts_data["por_geografia"]
                }]
            }
        }
    }
    return data