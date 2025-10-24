# mapaInteractivo/views.py
from django.shortcuts import render
from django.http import JsonResponse
from django.db.models import Count, Avg, Min, Max, Sum
from .models import Region, DatosComercializacion, Producto, Mercado
from django.db import models
import json

def mapa_interactivo(request):
    """Vista principal del mapa interactivo"""
    return render(request, 'mapaInteractivo/mapa.html')

def obtener_datos_region(request, region_id):
    """API para obtener datos de una región específica"""
    try:
        # Aquí irá la lógica para obtener datos de la región
        region = Region.objects.get(id=region_id)
        
        datos = {
            'region': region.nombre,
            'total_productos': 0,
            'productos': []
        }
        
        return JsonResponse(datos)
    
    except Region.DoesNotExist:
        return JsonResponse({'error': 'Región no encontrada'}, status=404)

def obtener_resumen_general(request):
    """API para obtener resumen general de todas las regiones"""
    try:
        # Estadísticas generales
        total_registros = DatosComercializacion.objects.count()
        total_regiones = Region.objects.count()
        total_productos = Producto.objects.count()
        
        datos = {
            'total_registros': total_registros,
            'total_regiones': total_regiones,
            'total_productos': total_productos,
        }
        
        return JsonResponse(datos)
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)