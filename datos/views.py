from django.shortcuts import render
from django.http import JsonResponse
from .models import PrecioDatos, Region, Producto

def estadisticas_rapidas(request):
    # Algunas estadísticas básicas
    total_registros = PrecioDatos.objects.count()
    total_regiones = Region.objects.count()
    total_productos = Producto.objects.count()
    
    # Últimos 10 registros
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
    # API simple para obtener datos
    datos = PrecioDatos.objects.select_related('region', 'mercado', 'producto')[:100]
    
    data = []
    for dato in datos:
        data.append({
            'fecha': dato.fecha.isoformat(),
            'region': dato.region.nombre,
            'mercado': dato.mercado.nombre,
            'producto': dato.producto.nombre,
            'variedad': dato.producto.variedad_tipo,
            'precio_promedio': float(dato.precio_promedio),
            'volumen': float(dato.volumen),
        })
    
    return JsonResponse(data, safe=False)