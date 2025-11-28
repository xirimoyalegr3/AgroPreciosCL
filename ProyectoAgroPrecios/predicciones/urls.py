# predicciones/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.prediccion_home, name='prediccion_home'),
]