from django.urls import path
from . import views

app_name = 'usuarios_front'

urlpatterns = [
    path('login/', views.login_view, name='login'),
]
