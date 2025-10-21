from django.shortcuts import render

# Create your views here.

def prediccion_view(request):
    return render(request, 'prediccion/prediccion.html')