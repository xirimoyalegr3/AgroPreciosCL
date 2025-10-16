from django.contrib import admin
from .models import Region, Mercado, Producto, PrecioDatos

@admin.register(Region)
class RegionAdmin(admin.ModelAdmin):
    list_display = ('id_region', 'nombre')
    search_fields = ('nombre',)

@admin.register(Mercado)
class MercadoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'region')
    list_filter = ('region',)
    search_fields = ('nombre',)

@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'variedad_tipo', 'subsector', 'calidad')
    list_filter = ('subsector', 'calidad')
    search_fields = ('nombre', 'variedad_tipo')

@admin.register(PrecioDatos)
class PrecioDatosAdmin(admin.ModelAdmin):
    list_display = ('fecha', 'producto', 'region', 'mercado', 'precio_promedio', 'volumen')
    list_filter = ('fecha', 'region', 'producto__subsector')
    search_fields = ('producto__nombre', 'region__nombre', 'mercado__nombre')
    date_hierarchy = 'fecha'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('producto', 'region', 'mercado')