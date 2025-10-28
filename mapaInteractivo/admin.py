# mapaInteractivo/admin.py
from django.contrib import admin
from .models import Region, Mercado, Subsector, Producto, Variedad, DatosComercializacion, ProgresoCarga

@admin.register(Region)
class RegionAdmin(admin.ModelAdmin):
    list_display = ['id_region', 'nombre', 'total_registros']
    search_fields = ['nombre']
    ordering = ['id_region']
    
    def total_registros(self, obj):
        return obj.datoscomercializacion_set.count()
    total_registros.short_description = 'Total Registros'

@admin.register(Mercado)
class MercadoAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'total_registros']
    search_fields = ['nombre']
    
    def total_registros(self, obj):
        return obj.datoscomercializacion_set.count()
    total_registros.short_description = 'Total Registros'

@admin.register(Subsector)
class SubsectorAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'total_registros', 'total_productos']
    search_fields = ['nombre']
    
    def total_registros(self, obj):
        return obj.datoscomercializacion_set.count()
    total_registros.short_description = 'Total Registros'
    
    def total_productos(self, obj):
        return obj.producto_set.count()
    total_productos.short_description = 'Total Productos'

@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'subsector', 'total_registros']
    list_filter = ['subsector']
    search_fields = ['nombre']
    
    def total_registros(self, obj):
        return obj.datoscomercializacion_set.count()
    total_registros.short_description = 'Total Registros'

@admin.register(Variedad)
class VariedadAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'producto', 'total_registros']
    list_filter = ['producto']
    search_fields = ['nombre', 'producto__nombre']
    
    def total_registros(self, obj):
        return obj.datoscomercializacion_set.count()
    total_registros.short_description = 'Total Registros'

@admin.register(DatosComercializacion)
class DatosComercializacionAdmin(admin.ModelAdmin):
    list_display = ['fecha', 'region', 'producto', 'precio_promedio', 'volumen', 'mercado']
    list_filter = ['fecha', 'region', 'subsector', 'producto', 'mercado']
    search_fields = ['producto__nombre', 'region__nombre']
    date_hierarchy = 'fecha'
    ordering = ['-fecha']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'region', 'producto', 'subsector', 'mercado'
        )

@admin.register(ProgresoCarga)
class ProgresoCargaAdmin(admin.ModelAdmin):
    list_display = ['archivo', 'completado', 'porcentaje', 'fecha_inicio', 'fecha_fin']
    list_filter = ['completado']
    readonly_fields = ['porcentaje', 'tiempo_transcurrido']
    ordering = ['-fecha_inicio']
    
    def porcentaje(self, obj):
        return f"{obj.get_porcentaje():.1f}%"
    porcentaje.short_description = 'Porcentaje'
    
    def tiempo_transcurrido(self, obj):
        if obj.fecha_fin:
            return obj.fecha_fin - obj.fecha_inicio
        return "En progreso"
    tiempo_transcurrido.short_description = 'Tiempo Transcurrido'

# Personalizacion del admin site
admin.site.site_header = "Administracion de Agro Precios Chile"
admin.site.site_title = "Agro Precios Chile"
admin.site.index_title = "Panel de Administracion"