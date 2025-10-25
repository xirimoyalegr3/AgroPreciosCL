# mapaInteractivo/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.mapa_interactivo, name='mapa_interactivo'),
    path('api/region/<int:region_id>/', views.obtener_datos_region, name='obtener_datos_region'),
    path('api/region/<int:region_id>/productos/', views.obtener_productos_region, name='obtener_productos_region'),
    path('api/resumen/', views.obtener_resumen_general, name='obtener_resumen_general'),
    path('api/filtros/', views.obtener_filtros_disponibles, name='obtener_filtros_disponibles'),
    path('api/subsector/<int:subsector_id>/productos/', views.obtener_productos_por_subsector, name='obtener_productos_por_subsector'),
]