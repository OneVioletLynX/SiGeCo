from calendar import monthrange
from datetime import date
from auditoria.models import RegistroAuditoria

MESES_ES = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun',
            'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic']


def _ultimos_seis_meses():
    hoy = date.today()
    meses = []
    for i in range(5, -1, -1):
        mes  = hoy.month - i
        anio = hoy.year
        while mes <= 0:
            mes  += 12
            anio -= 1
        meses.append((anio, mes))
    return meses


def get_admin_data():
    hoy        = date.today()
    inicio_mes = date(hoy.year, hoy.month, 1)

    qs_mes = RegistroAuditoria.objects.filter(fecha__date__gte=inicio_mes)

    altas          = qs_mes.filter(accion='ALTA').count()
    modificaciones = qs_mes.filter(accion='MODIFICACION').count()
    bajas          = qs_mes.filter(accion='BAJA').count()
    cobros         = qs_mes.filter(accion='COBRO').count()

    # Chart: altas por mes (últimos 6 meses)
    labels     = []
    data_altas = []
    for anio, mes in _ultimos_seis_meses():
        _, ultimo_dia = monthrange(anio, mes)
        inicio = date(anio, mes, 1)
        fin    = date(anio, mes, ultimo_dia)
        count  = RegistroAuditoria.objects.filter(
            fecha__date__gte=inicio,
            fecha__date__lte=fin,
            accion='ALTA',
        ).count()
        labels.append(MESES_ES[mes - 1])
        data_altas.append(count)

    return {
        "kpis": {
            "altas":          altas,
            "modificaciones": modificaciones,
            "bajas":          bajas,
            "cobros":         cobros,
        },
        "charts": {
            "chartAltasMensuales": {
                "title": {
                    "text":      "Altas mensuales",
                    "textStyle": {"color": "#355CC0"},
                    "top":       "10px",
                    "left":      "center",
                },
                "grid":   {"top": "60px", "bottom": "30px", "left": "40px", "right": "20px"},
                "xAxis":  {"type": "category", "data": labels},
                "yAxis":  {"type": "value", "minInterval": 1},
                "series": [{"name": "Altas", "data": data_altas, "type": "bar",
                             "itemStyle": {"color": "#355CC0"}}],
            }
        },
    }
