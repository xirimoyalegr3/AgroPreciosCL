# mapaInteractivo/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # Vista principal
    path('', views.mapa_interactivo, name='mapa_interactivo'),
    
    # APIs para datos de regiones
    path('api/region/<int:region_id>/', views.obtener_datos_region, name='obtener_datos_region'),
    path('api/region/<int:region_id>/productos/', views.obtener_productos_region, name='obtener_productos_region'),
    
    # APIs para filtros y datos generales
    path('api/resumen/', views.obtener_resumen_general, name='obtener_resumen_general'),
    path('api/filtros/', views.obtener_filtros_disponibles, name='obtener_filtros_disponibles'),
    path('api/subsector/<int:subsector_id>/productos/', views.obtener_productos_por_subsector, name='obtener_productos_por_subsector'),
    
    # Nueva API para comparacion de regiones
    path('api/comparar-regiones/', views.comparar_regiones, name='comparar_regiones'),
    
    # API para estadisticas avanzadas
    path('api/estadisticas/regiones/', views.estadisticas_regiones, name='estadisticas_regiones'),
    path('api/estadisticas/productos/', views.estadisticas_productos, name='estadisticas_productos'),
]