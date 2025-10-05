from django.urls import path
from . import views

urlpatterns = [
    path('estadisticas/', views.estadisticas_rapidas, name='estadisticas'),
    path('api/', views.api_datos, name='api_datos'),
]