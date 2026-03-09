from django.urls import path
from . import views

app_name = 'alumnos_front'

urlpatterns = [
    path('alumnos/', views.alumnos, name='alumnos'),
    path("alumnos/nuevo/", views.alumno_nuevo, name="alumno_nuevo"),
    path("<int:alumno_id>/", views.ficha_alumno,name="ficha_alumno"),
]
