from django.shortcuts import render

# Create your views here.
from django.shortcuts import render

def mapa_interactivo(request):
    return render(request, 'visualizacion/mapa.html')