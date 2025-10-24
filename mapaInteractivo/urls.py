# mapaInteractivo/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.mapa_interactivo, name='mapa_interactivo'),
    path('api/region/<int:region_id>/', views.obtener_datos_region, name='obtener_datos_region'),
    path('api/resumen/', views.obtener_resumen_general, name='obtener_resumen_general'),
]