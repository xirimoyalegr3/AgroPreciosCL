# mapaInteractivo/views.py
from django.shortcuts import render
from django.http import JsonResponse
from django.db.models import Count, Avg, Min, Max, Sum
from .models import Region, DatosComercializacion, Producto, Mercado, Subsector
from django.db import models
import json
from datetime import datetime

def mapa_interactivo(request):
    """Vista principal del mapa interactivo"""
    return render(request, 'mapaInteractivo/mapa.html')

# En mapaInteractivo/views.py - mejorar obtener_datos_region
def obtener_datos_region(request, region_id):
    """API para obtener datos REALES de una región específica"""
    try:
        # CORRECCIÓN: Usar id_region en lugar de id
        region = Region.objects.get(id_region=region_id)
        
        # Consultas REALES a la base de datos
        total_registros_region = DatosComercializacion.objects.filter(region=region).count()
        
        # Productos únicos en esta región
        productos_region = (DatosComercializacion.objects
                          .filter(region=region)
                          .values('producto__nombre')
                          .distinct()
                          .count())
        
        # Mercados en esta región
        mercados_region = (DatosComercializacion.objects
                          .filter(region=region)
                          .values('mercado__nombre')
                          .distinct()
                          .count())
        
        # Precios promedio por producto en esta región
        precios_promedio = (DatosComercializacion.objects
                           .filter(region=region)
                           .values('producto__nombre')
                           .annotate(
                               precio_promedio=Avg('precio_promedio'),
                               volumen_total=Sum('volumen')
                           )
                           .order_by('-volumen_total')[:10])
        
        # Subsectores en esta región
        subsectores = (DatosComercializacion.objects
                      .filter(region=region)
                      .values('subsector__nombre')  # Esto está bien
                      .annotate(total=Count('id'))
                      .order_by('-total'))
        
        # Convertir a formato correcto para el frontend
        subsectores_formateados = []
        for subsector in subsectores:
            subsectores_formateados.append({
                'nombre': subsector['subsector__nombre'],  # CORRECCIÓN: mapear correctamente
                'total': subsector['total']
            })
        
        datos = {
            'region_id': region.id_region,
            'region_nombre': region.nombre,
            'total_registros': total_registros_region,
            'total_productos': productos_region,
            'total_mercados': mercados_region,
            'subsectores': subsectores_formateados,  # Usar el formato corregido
            'productos_destacados': list(precios_promedio),
        }
        
        return JsonResponse(datos)
    
    except Region.DoesNotExist:
        return JsonResponse({'error': f'Región con ID {region_id} no encontrada'}, status=404)
    except Exception as e:
        return JsonResponse({'error': f'Error del servidor: {str(e)}'}, status=500)

        datos = {
            'region_id': region.id_region,  # CORRECCIÓN: Usar id_region
            'region_nombre': region.nombre,
            'total_registros': total_registros_region,
            'total_productos': productos_region,
            'total_mercados': mercados_region,
            'subsectores': list(subsectores),
            'productos_destacados': list(precios_promedio),
        }
        
        return JsonResponse(datos)
    
    except Region.DoesNotExist:
        return JsonResponse({'error': f'Región con ID {region_id} no encontrada'}, status=404)
    except Exception as e:
        return JsonResponse({'error': f'Error del servidor: {str(e)}'}, status=500)


def obtener_resumen_general(request):
    """API para obtener resumen general REAL de todas las regiones"""
    try:
        # Estadísticas generales REALES
        total_registros = DatosComercializacion.objects.count()
        total_regiones = Region.objects.count()
        total_productos = Producto.objects.count()
        total_mercados = Mercado.objects.count()
        
        # Fecha del registro más reciente
        fecha_reciente = (DatosComercializacion.objects
                         .order_by('-fecha')
                         .values('fecha')
                         .first())
        
        # Estadísticas por región
        estadisticas_regiones = (DatosComercializacion.objects
                                .values('region__id', 'region__nombre')
                                .annotate(
                                    total_registros=Count('id'),
                                    total_productos=Count('producto', distinct=True),
                                    precio_promedio_global=Avg('precio_promedio')
                                )
                                .order_by('-total_registros'))
        
        datos = {
            'total_registros': total_registros,
            'total_regiones': total_regiones,
            'total_productos': total_productos,
            'total_mercados': total_mercados,
            'fecha_reciente': fecha_reciente['fecha'] if fecha_reciente else None,
            'estadisticas_regiones': list(estadisticas_regiones),
        }
        
        return JsonResponse(datos)
    
    except Exception as e:
        return JsonResponse({'error': f'Error del servidor: {str(e)}'}, status=500)

def obtener_productos_region(request, region_id):
    """API para obtener lista de productos de una región con filtros"""
    try:
        region = Region.objects.get(id_region=region_id)
        
        # Parámetros de filtro
        subsector = request.GET.get('subsector', '')
        producto = request.GET.get('producto', '')
        año = request.GET.get('año', '')
        
        # Consulta base
        queryset = DatosComercializacion.objects.filter(region=region)
        
        # Aplicar filtros
        if subsector:
            queryset = queryset.filter(subsector__nombre__icontains=subsector)
        if producto:
            queryset = queryset.filter(producto__nombre__icontains=producto)
        if año:
            try:
                queryset = queryset.filter(fecha__year=int(año))
            except ValueError:
                pass  # Ignorar años inválidos
        
        # Agrupar por producto con estadísticas
        productos_data = (queryset
                         .values('producto__nombre', 'subsector__nombre')
                         .annotate(
                             total_registros=Count('id'),
                             precio_minimo=Min('precio_minimo'),
                             precio_maximo=Max('precio_maximo'),
                             precio_promedio=Avg('precio_promedio'),
                             volumen_total=Sum('volumen')
                         )
                         .order_by('-volumen_total')[:50])
        
        # DEBUG: Log para verificar datos
        print(f"Región {region_id}: {len(productos_data)} productos encontrados")
        if productos_data:
            print(f"Primer producto: {productos_data[0]}")
        
        datos = {
            'region': region.nombre,
            'filtros_aplicados': {
                'subsector': subsector,
                'producto': producto,
                'año': año
            },
            'total_resultados': len(productos_data),
            'productos': list(productos_data)
        }
        
        return JsonResponse(datos)
        
    except Region.DoesNotExist:
        return JsonResponse({'error': f'Región con ID {region_id} no encontrada'}, status=404)
    except Exception as e:
        print(f"Error en obtener_productos_region: {str(e)}")  # DEBUG
        return JsonResponse({'error': f'Error del servidor: {str(e)}'}, status=500) 

# En mapaInteractivo/views.py - mejorar obtener_filtros_disponibles
def obtener_filtros_disponibles(request):
    """API para obtener opciones de filtros disponibles"""
    try:
        # Años disponibles
        años = (DatosComercializacion.objects
                .dates('fecha', 'year')
                .order_by('-fecha'))
        
        # Subsectores
        subsectores = (Subsector.objects
                      .annotate(total=Count('datoscomercializacion'))
                      .values('id', 'nombre')
                      .order_by('-total'))
        
        # Productos más comunes (sin repetir)
        productos = (Producto.objects
                    .annotate(total=Count('datoscomercializacion'))
                    .values('id', 'nombre')
                    .order_by('nombre')  # Orden alfabético
                    .distinct())
        
        datos = {
            'años': [año.year for año in años],
            'subsectores': list(subsectores),
            'productos': list(productos),  # CORRECCIÓN: Todos los productos sin límite
        }
        
        return JsonResponse(datos)
        
    except Exception as e:
        return JsonResponse({'error': f'Error del servidor: {str(e)}'}, status=500)

# Nueva vista para obtener productos por subsector
def obtener_productos_por_subsector(request, subsector_id):
    """API para obtener productos de un subsector específico"""
    try:
        productos = (Producto.objects
                    .filter(subsector_id=subsector_id)
                    .values('id', 'nombre')
                    .order_by('nombre'))
        
        return JsonResponse({'productos': list(productos)})
        
    except Exception as e:
        return JsonResponse({'error': f'Error del servidor: {str(e)}'}, status=500)

# mapaInteractivo/views.py - AGREGAR esta vista
def obtener_productos_region(request, region_id):
    """API para obtener lista de productos de una región con filtros"""
    try:
        # CORRECCIÓN: Usar id_region en lugar de id
        region = Region.objects.get(id_region=region_id)
        
        # Parámetros de filtro
        subsector = request.GET.get('subsector', '')
        producto = request.GET.get('producto', '')
        año = request.GET.get('año', '')
        
        # Consulta base
        queryset = DatosComercializacion.objects.filter(region=region)
        
        # Aplicar filtros
        if subsector:
            queryset = queryset.filter(subsector__nombre__icontains=subsector)
        if producto:
            queryset = queryset.filter(producto__nombre__icontains=producto)
        if año:
            queryset = queryset.filter(fecha__year=int(año))
        
        # Agrupar por producto con estadísticas
        productos_data = (queryset
                         .values('producto__nombre', 'subsector__nombre')
                         .annotate(
                             total_registros=Count('id'),
                             precio_minimo=Min('precio_minimo'),
                             precio_maximo=Max('precio_maximo'),
                             precio_promedio=Avg('precio_promedio'),
                             volumen_total=Sum('volumen')
                         )
                         .order_by('-volumen_total')[:50])  # Limitar a 50 resultados
        
        datos = {
            'region': region.nombre,
            'filtros_aplicados': {
                'subsector': subsector,
                'producto': producto,
                'año': año
            },
            'total_resultados': len(productos_data),
            'productos': list(productos_data)
        }
        
        return JsonResponse(datos)
        
    except Region.DoesNotExist:
        return JsonResponse({'error': f'Región con ID {region_id} no encontrada'}, status=404)
    except Exception as e:
        return JsonResponse({'error': f'Error del servidor: {str(e)}'}, status=500)