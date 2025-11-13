from django.urls import path
from . import views

app_name = 'cobros_front'

urlpatterns = [
    path('cobros/', views.cobros, name='cobros'),
]
