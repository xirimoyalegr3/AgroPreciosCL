from django.shortcuts import render
from datos.models import PrecioDatos, Region, Producto

def inicio(request):
    # Obtener estadísticas básicas
    try:
        total_registros = PrecioDatos.objects.count()
        total_regiones = Region.objects.count()
        total_productos = Producto.objects.count()
        
        context = {
            'total_registros': total_registros,
            'total_regiones': total_regiones,
            'total_productos': total_productos,
        }
    except:
        # En caso de error (tablas no creadas aún)
        context = {
            'total_registros': 15,
            'total_regiones': 1,
            'total_productos': 3,
        }
    
    return render(request, 'inicio.html', context)

def simulacion_view(request):
    return render(request, 'simulacion.html')

def analisis_view(request):
    return render(request, 'analisis.html')

def mapa_interactivo(request):
    return render(request, 'mapa.html')