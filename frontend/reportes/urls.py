from django.urls import path
from . import views

app_name = 'reportes'

urlpatterns = [
    path('',                views.reportes_index,       name='reportes_index'),
    path('estadisticas',    views.dashboard_estadisticas, name='estadisticas'),
    path('reportes_alumnos', views.reportes_alumnos,    name='reportes_alumnos'),
    path('reportes_bonos',       views.reportes_bonos,       name='reportes_bonos'),
    path('reportes_demografico', views.reportes_demografico, name='reportes_demografico'),
]