from django.shortcuts import render
from django.http import JsonResponse
from django.db.models import Avg

from .models import PrecioDatos, Region, Mercado, Producto


def estadisticas_rapidas(request):
    """
    Vista que muestra estadísticas básicas y últimos registros.
    """
    total_registros = PrecioDatos.objects.count()
    total_regiones = Region.objects.count()
    total_productos = Producto.objects.count()
    
    ultimos_registros = PrecioDatos.objects.select_related(
        'region', 'mercado', 'producto'
    ).order_by('-fecha')[:10]
    
    context = {
        'total_registros': total_registros,
        'total_regiones': total_regiones,
        'total_productos': total_productos,
        'ultimos_registros': ultimos_registros,
    }
    return render(request, 'datos/estadisticas.html', context)


def api_datos(request):
    """
    API simple que devuelve los primeros 100 registros de PrecioDatos en JSON.
    """
    datos = PrecioDatos.objects.select_related('region', 'mercado', 'producto')[:100]
    
    data = [
        {
            'fecha': dato.fecha.isoformat(),
            'region': dato.region.nombre,
            'mercado': dato.mercado.nombre,
            'producto': dato.producto.nombre,
            'variedad': dato.producto.variedad_tipo,
            'precio_promedio': float(dato.precio_promedio),
            'volumen': float(dato.volumen),
        }
        for dato in datos
    ]
    
    return JsonResponse(data, safe=False)


def mapa(request):
    """
    Vista para el mapa interactivo, mostrando KPIs y tabla de datos.
    """
    # KPIs
    mayor_variacion = PrecioDatos.objects.order_by('-precio_promedio').first()
    
    region_mas_cara = PrecioDatos.objects.values('region__nombre') \
        .annotate(avg_precio=Avg('precio_promedio')) \
        .order_by('-avg_precio').first()
    
    mercado_top = PrecioDatos.objects.values('mercado__nombre') \
        .annotate(avg_precio=Avg('precio_promedio')) \
        .order_by('-avg_precio').first()
    
    # Tabla de resultados
    resultados = PrecioDatos.objects.select_related('region', 'mercado', 'producto')[:10]

    context = {
        'mayor_variacion': mayor_variacion,
        'region_mas_cara': region_mas_cara,
        'mercado_top': mercado_top,
        'resultados': resultados,
        'datos_bd': resultados,
    }
    
    return render(request, 'mapa.html', context)
