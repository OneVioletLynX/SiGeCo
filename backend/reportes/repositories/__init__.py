from .contabilidad_repo import get_kpis_cont, get_charts_cont
from .alumnos_repo import get_kpis_alumnos, get_charts_alumnos
from .admin_repo import get_kpis_admin, get_charts_admin

__all__ = [
    "get_kpis_cont",
    "get_charts_cont",
    "get_kpis_alumnos",
    "get_charts_alumnos",
    "get_kpis_admin",
    "get_charts_admin",
]
