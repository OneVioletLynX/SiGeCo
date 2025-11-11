from django.urls import path
from . import views

app_name = 'cobros'

urlpatterns = [
    path('cobros/', views.cobros, name='cobros'),
]
