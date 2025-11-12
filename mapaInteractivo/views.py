# mapaInteractivo/views.py
from django.shortcuts import render
from django.http import JsonResponse
from django.db.models import Count, Avg, Min, Max, Sum, F
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

def obtener_resumen_general(request):
    """API para obtener resumen general REAL de todas las regiones"""
    try:
        # Estadísticas generales REALES
        total_registros = DatosComercializacion.objects.count()
        total_regiones = Region.objects.count()
        total_productos = Producto.objects.count()
        total_mercados = Mercado.objects.count()

        # Fecha del registro más reciente
        ultimo_registro = DatosComercializacion.objects.order_by('-fecha').first()
        fecha_reciente = ultimo_registro.fecha if ultimo_registro else None

        # Estadísticas por región
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

def obtener_filtros_disponibles(request):
    """API para obtener opciones de filtros disponibles"""
    try:
        with transaction.atomic():
            # Años disponibles
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

# DASHBOARD CON SOLO DATOS REALES
def dashboard_analisis(request):
    """API principal para el dashboard - SOLO DATOS REALES"""
    try:
        with transaction.atomic():
            # Métricas principales - DATOS REALES
            metricas_principales = calcular_metricas_principales_reales()

            # Análisis de precios - DATOS REALES
            analisis_precios = calcular_analisis_precios_reales()

            # Análisis de volúmenes - DATOS REALES
            analisis_volumenes = calcular_analisis_volumenes_reales()

            # Oportunidades de mercado - DATOS REALES
            oportunidades_mercado = identificar_oportunidades_mercado_reales()

            # Análisis temporal - DATOS REALES
            analisis_temporal = calcular_analisis_temporal_reales()

            datos = {
                'metricas_principales': metricas_principales,
                'analisis_precios': analisis_precios,
                'analisis_volumenes': analisis_volumenes,
                'oportunidades_mercado': oportunidades_mercado,
                'analisis_temporal': analisis_temporal,
            }

            return JsonResponse(datos)

    except Exception as e:
        logger.error(f"Error en dashboard_analisis: {str(e)}")
        # Si hay error, retornar estructura vacía pero NO datos falsos
        return JsonResponse({
            'metricas_principales': {},
            'analisis_precios': {'top_oportunidades': []},
            'analisis_volumenes': {'top_regiones_volumen': []},
            'oportunidades_mercado': [],
            'analisis_temporal': {'estacionalidad_productos': []},
        }, status=500)

def calcular_metricas_principales_reales():
    """Métricas calculadas solo con datos reales de la BD -  """
    try:
        #  Margen potencial promedio -  
        productos_margen = (DatosComercializacion.objects
                           .values('producto__nombre')
                           .annotate(
                               precio_max=Max('precio_promedio'),
                               precio_min=Min('precio_promedio'),
                               total_reg=Count('id')
                           )
                           .filter(precio_min__gt=0, total_reg__gt=0))  #  
        
        margenes_validos = []
        for producto in productos_margen:
            try:
                margen = ((producto['precio_max'] - producto['precio_min']) / 
                         producto['precio_min'] * 100)
                if margen < 100000:  #   con outliers
                    margenes_validos.append(margen)
            except (ZeroDivisionError, TypeError):
                continue
        
        margen_promedio = sum(margenes_validos) / len(margenes_validos) if margenes_validos else 0
        
        #  Productos con alto margen (>20%) -  
        productos_alto_margen = len([m for m in margenes_validos if m > 20])
        
        #  Regiones activas -  
        regiones_activas = (DatosComercializacion.objects
                           .values('region__nombre')
                           .annotate(total_registros=Count('id'))
                           .filter(total_registros__gt=0)  
                           .count())
        
        #  Estacionalidad promedio 
        try:
            variacion_mensual = (DatosComercializacion.objects
                                .values('fecha__month')
                                .annotate(
                                    avg_precio=Avg('precio_promedio'),
                                    total_reg=Count('id')
                                )
                                .filter(total_reg__gt=0)) 
            
            if len(variacion_mensual) > 1:
                precios_mensuales = [item['avg_precio'] for item in variacion_mensual if item['avg_precio']]
                if precios_mensuales:
                    precio_max = max(precios_mensuales)
                    precio_min = min(precios_mensuales)
                    estacionalidad = ((precio_max - precio_min) / precio_min * 100) if precio_min > 0 else 0
                else:
                    estacionalidad = 0
            else:
                estacionalidad = 0
        except:
            estacionalidad = 0
        
        return {
            'margen_potencial_promedio': round(margen_promedio, 1),
            'productos_alto_margen': productos_alto_margen,
            'regiones_activas': regiones_activas,
            'estacionalidad_promedio': round(estacionalidad, 1),
        }
    except Exception as e:
        logger.error(f"Error en métricas principales: {str(e)}")
        return {}

def calcular_analisis_precios_reales():
    """Análisis de precios con datos reales - PARÁMETROS  S"""
    try:
        # Productos con diferencial de precio - PARÁMETROS  S
        productos_diferencial = (DatosComercializacion.objects
                               .values('producto__nombre')
                               .annotate(
                                   precio_maximo=Max('precio_promedio'),
                                   precio_minimo=Min('precio_promedio'),
                                   region_maximo=Max('region__nombre'),
                                   region_minimo=Min('region__nombre'),
                                   total_registros=Count('id'),
                                   avg_precio=Avg('precio_promedio')
                               )
                               .filter(
                                   total_registros__gt=1, #  : solo 1 registro
                                   precio_minimo__gt=0,
                                   precio_maximo__lt=1000000 #  
                               )
                               .order_by('-precio_maximo')[:10]) # Más resultados

        top_oportunidades = []
        for producto in productos_diferencial:
            try:
                margen_potencial = ((producto['precio_maximo'] - producto['precio_minimo']) /
                                   producto['precio_minimo'] * 100)

                # Menos restrictivo con outliers
                if margen_potencial < 100000: #  
                    # Formatear precios para mejor visualización
                    def formatear_precio(precio):
                        if precio >= 1000000:
                            return f"${precio/1000000:.1f}M"
                        elif precio >= 1000:
                            return f"${precio/1000:.1f}K"
                        return f"${precio:.0f}"

                    top_oportunidades.append({
                        'producto': producto['producto__nombre'],
                        'mejor_region': producto['region_maximo'],
                        'peor_region': producto['region_minimo'],
                        'precio_maximo': formatear_precio(producto['precio_maximo']),
                        'precio_minimo': formatear_precio(producto['precio_minimo']),
                        'diferencial_precio': formatear_precio(producto['precio_maximo'] - producto['precio_minimo']),
                        'margen_potencial': round(float(margen_potencial), 1)
                    })
            except (ZeroDivisionError, TypeError):
                continue

        return {
            'top_oportunidades': top_oportunidades
        }
    except Exception as e:
        logger.error(f"Error en análisis de precios: {str(e)}")
        return {'top_oportunidades': []}

def calcular_analisis_volumenes_reales():
    """Análisis de volúmenes con datos reales"""
    try:
        regiones_volumen = (DatosComercializacion.objects
                           .values('region__nombre')
                           .annotate(
                               volumen_total=Sum('volumen'),
                               productos_unicos=Count('producto', distinct=True),
                               mercados_activos=Count('mercado', distinct=True),
                               total_registros=Count('id')
                           )
                           .filter(volumen_total__isnull=False)
                           .order_by('-volumen_total')[:6])

        top_regiones_volumen = []
        for region in regiones_volumen:
            try:
                # Producto más transado en la región - DATO REAL
                producto_mas_transado = (DatosComercializacion.objects
                                       .filter(region__nombre=region['region__nombre'])
                                       .values('producto__nombre')
                                       .annotate(total_volumen=Sum('volumen'))
                                       .order_by('-total_volumen')
                                       .first())

                # Liquidez - CALCULO REAL
                liquidez = (region['total_registros'] / region['productos_unicos']
                           if region['productos_unicos'] > 0 else 0)

                # Formatear volumen
                def formatear_volumen(volumen):
                    if volumen >= 1000000:
                        return f"{volumen/1000000:.1f}M"
                    elif volumen >= 1000:
                        return f"{volumen/1000:.1f}K"
                    return f"{volumen:.0f}"

                top_regiones_volumen.append({
                    'region': region['region__nombre'],
                    'producto_mas_transado': (producto_mas_transado['producto__nombre']
                                             if producto_mas_transado else 'Sin datos'),
                    'volumen_total': formatear_volumen(float(region['volumen_total'] or 0)),
                    'mercados_activos': region['mercados_activos'],
                    'liquidez': round(liquidez, 1)
                })
            except (TypeError, KeyError):
                continue

        return {
            'top_regiones_volumen': top_regiones_volumen
        }
    except Exception as e:
        logger.error(f"Error en análisis de volúmenes: {str(e)}")
        return {'top_regiones_volumen': []}

def identificar_oportunidades_mercado_reales():
    """Oportunidades basadas en datos reales -  """
    try:
        oportunidades = []

        #  Productos con variación de precios -  
        productos_variacion = (DatosComercializacion.objects
                              .values('producto__nombre')
                              .annotate(
                                  variacion=((Max('precio_promedio') - Min('precio_promedio')) / Min('precio_promedio') * 100),
                                  total_registros=Count('id'),
                                  avg_precio=Avg('precio_promedio')
                              )
                              .filter(
                                  variacion__gt=10, #  : 10% en lugar de 20%
                                  variacion__lt=10000, #  
                                  total_registros__gt=1, #  
                                  avg_precio__lt=50000 #  
                              )
                              .order_by('-variacion')[:5]) # Más resultados

        for producto in productos_variacion:
            potencial = 'Alto' if producto['variacion'] > 100 else 'Medio' if producto['variacion'] > 30 else 'Bajo'

            oportunidades.append({
                'tipo': 'Arbitraje Regional',
                'descripcion': f"{producto['producto__nombre']} - Variación {producto['variacion']:.1f}%",
                'potencial': potencial,
                'riesgo': 'Medio',
                'recomendacion': 'Comprar en regiones de bajo precio, vender en regiones de alto precio'
            })

        #  Productos con buen volumen y precio estable
        productos_volumen = (DatosComercializacion.objects
                           .values('producto__nombre')
                           .annotate(
                               volumen_total=Sum('volumen'),
                               precio_promedio=Avg('precio_promedio'),
                               total_registros=Count('id'),
                               regiones_activas=Count('region', distinct=True)
                           )
                           .filter(
                               volumen_total__gt=1000,
                               total_registros__gt=2,
                               regiones_activas__gt=1
                           )
                           .order_by('-volumen_total')[:3])

        for producto in productos_volumen:
            oportunidades.append({
                'tipo': 'Mercado Estable',
                'descripcion': f"{producto['producto__nombre']} - Alto volumen ({producto['volumen_total']:.0f})",
                'potencial': 'Medio',
                'riesgo': 'Bajo',
                'recomendacion': 'Mercado estable con buena liquidez'
            })

        return oportunidades

    except Exception as e:
        logger.error(f"Error identificando oportunidades: {str(e)}")
        return []

def calcular_analisis_temporal_reales():
    """Análisis temporal con datos reales -  """
    try:
        # Calcular estacionalidad real por producto -  
        productos_estacionalidad = (DatosComercializacion.objects
                                  .values('producto__nombre')
                                  .annotate(
                                      total_registros=Count('id'),
                                      variacion_mensual=((Max('precio_promedio') - Min('precio_promedio')) / Min('precio_promedio') * 100),
                                      meses_activos=Count('fecha__month', distinct=True)
                                  )
                                  .filter(
                                      total_registros__gt=2, #  
                                      variacion_mensual__lt=100000, #  
                                      meses_activos__gt=1 # Al menos 2 meses diferentes
                                  )
                                  .order_by('-variacion_mensual')[:8]) # Más resultados

        estacionalidad_productos = []
        for producto in productos_estacionalidad:
            # Análisis básico por mes
            meses_data = (DatosComercializacion.objects
                         .filter(producto__nombre=producto['producto__nombre'])
                         .values('fecha__month')
                         .annotate(
                             avg_precio=Avg('precio_promedio'),
                             total_reg=Count('id')
                         )
                         .order_by('fecha__month'))

            if meses_data:
                # Encontrar mes con precio más bajo y más alto
                mes_min = min(meses_data, key=lambda x: x['avg_precio'])
                mes_max = max(meses_data, key=lambda x: x['avg_precio'])

                meses_nombres = {
                    1: 'Enero', 2: 'Febrero', 3: 'Marzo', 4: 'Abril',
                    5: 'Mayo', 6: 'Junio', 7: 'Julio', 8: 'Agosto',
                    9: 'Septiembre', 10: 'Octubre', 11: 'Noviembre', 12: 'Diciembre'
                }

                mejor_comprar = meses_nombres.get(mes_min['fecha__month'], 'Analizar')
                mejor_vender = meses_nombres.get(mes_max['fecha__month'], 'Analizar')
            else:
                mejor_comprar = 'Analizar'
                mejor_vender = 'Analizar'

            # Determinar tendencia
            tendencia_data = (DatosComercializacion.objects
                            .filter(producto__nombre=producto['producto__nombre'])
                            .order_by('fecha'))

            if tendencia_data.count() > 1:
                primer_precio = tendencia_data.first().precio_promedio
                ultimo_precio = tendencia_data.last().precio_promedio

                if primer_precio and ultimo_precio and primer_precio > 0:
                    tendencia_porcentaje = ((ultimo_precio - primer_precio) / primer_precio * 100)
                    if tendencia_porcentaje > 5:
                        tendencia = 'Alcista'
                    elif tendencia_porcentaje < -5:
                        tendencia = 'Bajista'
                    else:
                        tendencia = 'Estable'
                else:
                    tendencia = 'Estable'
            else:
                tendencia = 'Estable'

            estacionalidad_productos.append({
                'producto': producto['producto__nombre'],
                'mejor_mes_comprar': mejor_comprar,
                'mejor_mes_vender': mejor_vender,
                'variacion_estacional': round(producto['variacion_mensual'], 1),
                'tendencia': tendencia
            })

        return {
            'estacionalidad_productos': estacionalidad_productos
        }
    except Exception as e:
        logger.error(f"Error en análisis temporal: {str(e)}")
        return {'estacionalidad_productos': []}

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