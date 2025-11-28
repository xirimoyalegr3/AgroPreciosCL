# AgroPreciosChile/urls.py (proyecto principal)
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('mapaInteractivo.urls')),
    path('predicciones/', include('predicciones.urls')),
    path('select2/', include('django_select2.urls')),
]