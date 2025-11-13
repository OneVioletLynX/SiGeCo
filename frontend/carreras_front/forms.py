from django import forms
from backend.carreras.models import Carrera  # 👈 importás el modelo del backend

class CarreraForm(forms.ModelForm):
    class Meta:
        model = Carrera
        fields = ['descripcion']
