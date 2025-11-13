from reportes.repositories.contabilidad_repo import get_kpis_cont, get_charts_cont


def get_contabilidad_data():
    data_kpis = get_kpis_cont()
    kpis = data_kpis["kpis"]
    data_charts = get_charts_cont()
    
    data = {
        "kpis": kpis,
        "charts": {
            # --- Ingresos Mensuales ---
            "chartIngresos": {
                "title": {"text": "Ingresos Mensuales", "textStyle": {"color": "#355CC0"},"top": "10px", "left": "center"},
                "grid": {"top": "60px", "bottom": "30px", "left": "80px", "right": "20px"},
                "xAxis": {"data": data_charts["meses_ingresos"]},
                "yAxis": {"type": "value"},
                "series": [{"data": data_charts["ingresos_mensuales"], "type": "bar"}]
            },
            # --- Distribución de medios de pago ---
            "chartMediosPago": {
                "title": {"text": "Distribución de medios de pago", "textStyle": {"color": "#355CC0", "fontSize": 14},"top": "10px", "left": "center"},
                "grid": {"top": "60px", "bottom": "30px", "left": "20px", "right": "20px"},
                "tooltip": {"trigger": "item"},
                "legend": {
                    "orient": 'vertical',
                    "left": 'left',
                    "bottom": "10px",
                    "data": [item['name'] for item in data_charts["medios_pago"]]
                },
                "series": [{
                    "type": "pie",
                    "radius": "50%",
                    "data": data_charts["medios_pago"]
                }]
            },
            # --- Deuda promedio por alumno ---
            "chartDeudaPromedio": {
                "title": {"text": "Deuda promedio por alumno", "textStyle": {"color": "#355CC0", "fontSize": 16},"top": "10px", "left": "center"},
                "grid": {"top": 60, "right": 10, "bottom": 140, "left": 80}, 
                "xAxis": {
                    "type": "category", 
                    "data": data_charts["carreras"], 
                    "axisLabel": {
                        "rotate": 45,
                        "interval": 0,
                        "overflow": "breakAll",
                        "fontSize": 8
                    }
                },
                "yAxis": {"type": "value"},
                "series": [{"data": data_charts["deuda_promedio"], "type": "bar"}] 
            },
            # --- Demora promedio en pagos (días) ---
            "chartDemoraPagos": {
                "title": {
                    "text": "Demora promedio en pagos (días)", "top": "10px", "left": "center", 
                    "textStyle": {"color": "#355CC0", "fontSize": 14}
                },
                "grid": {"top": "60px", "bottom": "30px", "left": "60px", "right": "20px"},
                "xAxis": {"type": "category", "data": data_charts["meses_demora"]},
                "yAxis": {"type": "value"},
                "series": [{"data": data_charts["demora_mensual"], "type": "line", "smooth": True, "bottom": "10px"}]
            }
        }
    }
    return data