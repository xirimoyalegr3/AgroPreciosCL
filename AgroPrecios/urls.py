from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.inicio, name='inicio'),
    path('simulacion/', views.simulacion_view, name='simulacion'),
    path('analisis/', views.analisis_view, name='analisis'),
    path('mapa/', views.mapa_interactivo, name='mapa'),
    path('datos/', include('datos.urls')),  # ¡Descomentar esta línea!

]