from django.shortcuts import render

# Create your views here.

def simulacion_view(request):
    return render(request, 'simulacion/simulacion.html')