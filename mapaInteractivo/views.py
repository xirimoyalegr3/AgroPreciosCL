# mapaInteractivo/views.py
from django.shortcuts import render
from django.http import JsonResponse
from django.db.models import Count, Avg, Min, Max, Sum
from django.db import transaction
from .models import Region, DatosComercializacion, Producto, Mercado, Subsector
import logging

logger = logging.getLogger(__name__)

def mapa_interactivo(request):
    """Vista principal del mapa interactivo"""
    try:
        return render(request, 'mapaInteractivo/mapa.html')
    except Exception as e:
        logger.error(f"Error en vista mapa_interactivo: {str(e)}")
        return render(request, 'mapaInteractivo/error.html', {'error': str(e)})

def obtener_datos_region(request, region_id):
    """API para obtener datos REALES de una region especifica"""
    try:
        with transaction.atomic():
            region = Region.objects.get(id_region=region_id)
            
            total_registros_region = DatosComercializacion.objects.filter(region=region).count()
            
            productos_region = (DatosComercializacion.objects
                              .filter(region=region)
                              .values('producto__nombre')
                              .distinct()
                              .count())
            
            mercados_region = (DatosComercializacion.objects
                              .filter(region=region)
                              .values('mercado__nombre')
                              .distinct()
                              .count())
            
            precios_promedio = (DatosComercializacion.objects
                               .filter(region=region)
                               .values('producto__nombre')
                               .annotate(
                                   precio_promedio=Avg('precio_promedio'),
                                   volumen_total=Sum('volumen')
                               )
                               .order_by('-volumen_total')[:10])
            
            subsectores = (DatosComercializacion.objects
                          .filter(region=region)
                          .values('subsector__nombre')
                          .annotate(total=Count('id'))
                          .order_by('-total'))
            
            subsectores_formateados = []
            for subsector in subsectores:
                subsectores_formateados.append({
                    'nombre': subsector['subsector__nombre'],
                    'total': subsector['total']
                })
            
            datos = {
                'region_id': region.id_region,
                'region_nombre': region.nombre,
                'total_registros': total_registros_region,
                'total_productos': productos_region,
                'total_mercados': mercados_region,
                'subsectores': subsectores_formateados,
                'productos_destacados': list(precios_promedio),
            }
            
            return JsonResponse(datos)
    
    except Region.DoesNotExist:
        logger.warning(f"Region con ID {region_id} no encontrada")
        return JsonResponse({'error': f'Region con ID {region_id} no encontrada'}, status=404)
    except Exception as e:
        logger.error(f"Error en obtener_datos_region: {str(e)}")
        return JsonResponse({'error': f'Error del servidor: {str(e)}'}, status=500)

# mapaInteractivo/views.py - CORREGIR obtener_resumen_general
def obtener_resumen_general(request):
    """API para obtener resumen general REAL de todas las regiones"""
    try:
        # Estadísticas generales REALES
        total_registros = DatosComercializacion.objects.count()
        total_regiones = Region.objects.count()
        total_productos = Producto.objects.count()
        total_mercados = Mercado.objects.count()
        
        # Fecha del registro más reciente - CORREGIDO
        ultimo_registro = DatosComercializacion.objects.order_by('-fecha').first()
        fecha_reciente = ultimo_registro.fecha if ultimo_registro else None
        
        # Estadísticas por región - CORREGIDO: usar id_region en lugar de id
        estadisticas_regiones = (DatosComercializacion.objects
                                .values('region__id_region', 'region__nombre')
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
            'fecha_reciente': fecha_reciente.isoformat() if fecha_reciente else None,
            'estadisticas_regiones': list(estadisticas_regiones),
        }
        
        return JsonResponse(datos)
    
    except Exception as e:
        logger.error(f"Error en obtener_resumen_general: {str(e)}")
        return JsonResponse({'error': f'Error del servidor: {str(e)}'}, status=500)

def obtener_productos_region(request, region_id):
    """API para obtener lista de productos de una region con filtros"""
    try:
        with transaction.atomic():
            region = Region.objects.get(id_region=region_id)
            
            subsector = request.GET.get('subsector', '')
            producto = request.GET.get('producto', '')
            año = request.GET.get('año', '')
            
            queryset = DatosComercializacion.objects.filter(region=region)
            
            if subsector:
                queryset = queryset.filter(subsector__nombre__icontains=subsector)
            if producto:
                queryset = queryset.filter(producto__nombre__icontains=producto)
            if año:
                try:
                    queryset = queryset.filter(fecha__year=int(año))
                except ValueError:
                    pass
            
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
        logger.warning(f"Region con ID {region_id} no encontrada")
        return JsonResponse({'error': f'Region con ID {region_id} no encontrada'}, status=404)
    except Exception as e:
        logger.error(f"Error en obtener_productos_region: {str(e)}")
        return JsonResponse({'error': f'Error del servidor: {str(e)}'}, status=500)

# En mapaInteractivo/views.py - corregir obtener_filtros_disponibles
def obtener_filtros_disponibles(request):
    """API para obtener opciones de filtros disponibles"""
    try:
        with transaction.atomic():
            # Años disponibles - CORREGIDO: evitar duplicados
            años = (DatosComercializacion.objects
                    .dates('fecha', 'year', order='DESC')
                    .distinct())
            
            años_lista = [año.year for año in años]
            
            # Subsectores
            subsectores = (Subsector.objects
                          .annotate(total=Count('datoscomercializacion'))
                          .values('id', 'nombre')
                          .order_by('-total'))
            
            # Productos
            productos = (Producto.objects
                        .annotate(total=Count('datoscomercializacion'))
                        .values('id', 'nombre')
                        .order_by('nombre')
                        .distinct())
            
            datos = {
                'años': años_lista,
                'subsectores': list(subsectores),
                'productos': list(productos),
            }
            
            return JsonResponse(datos)
            
    except Exception as e:
        logger.error(f"Error en obtener_filtros_disponibles: {str(e)}")
        return JsonResponse({'error': f'Error del servidor: {str(e)}'}, status=500)

def obtener_productos_por_subsector(request, subsector_id):
    """API para obtener productos de un subsector especifico"""
    try:
        with transaction.atomic():
            productos = (Producto.objects
                        .filter(subsector_id=subsector_id)
                        .values('id', 'nombre')
                        .order_by('nombre'))
            
            return JsonResponse({'productos': list(productos)})
            
    except Exception as e:
        logger.error(f"Error en obtener_productos_por_subsector: {str(e)}")
        return JsonResponse({'error': f'Error del servidor: {str(e)}'}, status=500)

# mapaInteractivo/views.py (funciones adicionales)
def estadisticas_regiones(request):
    """API para obtener estadisticas comparativas de todas las regiones"""
    try:
        with transaction.atomic():
            estadisticas = (DatosComercializacion.objects
                           .values('region__id_region', 'region__nombre')
                           .annotate(
                               total_registros=Count('id'),
                               total_productos=Count('producto', distinct=True),
                               total_mercados=Count('mercado', distinct=True),
                               precio_promedio=Avg('precio_promedio'),
                               volumen_total=Sum('volumen')
                           )
                           .order_by('region__id_region'))
            
            return JsonResponse({
                'estadisticas': list(estadisticas),
                'total_regiones': len(estadisticas)
            })
            
    except Exception as e:
        logger.error(f"Error en estadisticas_regiones: {str(e)}")
        return JsonResponse({'error': f'Error del servidor: {str(e)}'}, status=500)

def estadisticas_productos(request):
    """API para obtener estadisticas de productos a nivel nacional"""
    try:
        with transaction.atomic():
            producto = request.GET.get('producto', '')
            subsector = request.GET.get('subsector', '')
            año = request.GET.get('año', '')
            
            queryset = DatosComercializacion.objects.all()
            
            if producto:
                queryset = queryset.filter(producto__nombre__icontains=producto)
            if subsector:
                queryset = queryset.filter(subsector__nombre__icontains=subsector)
            if año:
                try:
                    queryset = queryset.filter(fecha__year=int(año))
                except ValueError:
                    pass
            
            estadisticas = (queryset
                           .values('producto__nombre', 'subsector__nombre')
                           .annotate(
                               total_registros=Count('id'),
                               regiones_activas=Count('region', distinct=True),
                               precio_minimo=Min('precio_minimo'),
                               precio_maximo=Max('precio_maximo'),
                               precio_promedio=Avg('precio_promedio'),
                               volumen_total=Sum('volumen')
                           )
                           .order_by('-volumen_total')[:100])
            
            return JsonResponse({
                'estadisticas': list(estadisticas),
                'filtros_aplicados': {
                    'producto': producto,
                    'subsector': subsector,
                    'año': año
                }
            })
            
    except Exception as e:
        logger.error(f"Error en estadisticas_productos: {str(e)}")
        return JsonResponse({'error': f'Error del servidor: {str(e)}'}, status=500)

        
def comparar_regiones(request):
    """API para comparar multiples regiones"""
    try:
        region_ids = request.GET.get('regiones', '')
        if not region_ids:
            return JsonResponse({'error': 'No se especificaron regiones para comparar'}, status=400)
        
        region_ids = [int(id) for id in region_ids.split(',') if id.isdigit()]
        
        with transaction.atomic():
            datos_comparativos = []
            
            for region_id in region_ids:
                try:
                    region = Region.objects.get(id_region=region_id)
                    
                    # Estadísticas básicas de la región
                    total_registros = DatosComercializacion.objects.filter(region=region).count()
                    productos_unicos = DatosComercializacion.objects.filter(region=region).values('producto').distinct().count()
                    mercados_unicos = DatosComercializacion.objects.filter(region=region).values('mercado').distinct().count()
                    
                    # Estadísticas de precios y volumen
                    estadisticas = DatosComercializacion.objects.filter(region=region).aggregate(
                        precio_promedio=Avg('precio_promedio'),
                        volumen_total=Sum('volumen')
                    )
                    
                    datos_comparativos.append({
                        'region_id': region.id_region,
                        'region_nombre': region.nombre,
                        'estadisticas': {
                            'total_registros': total_registros,
                            'productos_unicos': productos_unicos,
                            'total_mercados': mercados_unicos,
                            'precio_promedio': float(estadisticas['precio_promedio']) if estadisticas['precio_promedio'] else 0,
                            'volumen_total': float(estadisticas['volumen_total']) if estadisticas['volumen_total'] else 0
                        }
                    })
                    
                except Region.DoesNotExist:
                    continue
            
            return JsonResponse({
                'regiones_comparadas': datos_comparativos,
                'total_regiones': len(datos_comparativos)
            })
            
    except Exception as e:
        logger.error(f"Error en comparar_regiones: {str(e)}")
        return JsonResponse({'error': f'Error del servidor: {str(e)}'}, status=500)
            

    except Exception as e:
        logger.error(f"Error en comparar_regiones: {str(e)}")
        return JsonResponse({'error': f'Error del servidor: {str(e)}'}, status=500)