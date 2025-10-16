from django.db import models

class Region(models.Model):
    id_region = models.PositiveIntegerField(unique=True)
    nombre = models.CharField(max_length=100, db_index=True)

    class Meta:
        ordering = ['nombre']
        verbose_name = "Región"
        verbose_name_plural = "Regiones"

    def __str__(self):
        return self.nombre


class Mercado(models.Model):
    nombre = models.CharField(max_length=200, db_index=True)
    region = models.ForeignKey(Region, on_delete=models.CASCADE, related_name='mercados')

    class Meta:
        ordering = ['nombre']
        verbose_name = "Mercado"
        verbose_name_plural = "Mercados"

    def __str__(self):
        return self.nombre


class Producto(models.Model):
    subsector = models.CharField(max_length=100, db_index=True)
    nombre = models.CharField(max_length=200, db_index=True)
    variedad_tipo = models.CharField(max_length=100, blank=True, null=True)
    calidad = models.CharField(max_length=50, blank=True, null=True)
    unidad_comercializacion = models.CharField(max_length=100, blank=True, null=True)
    origen = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        ordering = ['nombre']
        verbose_name = "Producto"
        verbose_name_plural = "Productos"

    def __str__(self):
        return f"{self.nombre} - {self.variedad_tipo or 'Sin tipo'}"


class PrecioDatos(models.Model):
    fecha = models.DateField(db_index=True)
    region = models.ForeignKey(Region, on_delete=models.CASCADE, related_name='precios_region')
    mercado = models.ForeignKey(Mercado, on_delete=models.CASCADE, related_name='precios_mercado')
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name='precios_producto')
    volumen = models.DecimalField(max_digits=15, decimal_places=2)
    precio_minimo = models.DecimalField(max_digits=12, decimal_places=4)
    precio_maximo = models.DecimalField(max_digits=12, decimal_places=4)
    precio_promedio = models.DecimalField(max_digits=12, decimal_places=4)

    class Meta:
        indexes = [
            models.Index(fields=['fecha']),
            models.Index(fields=['region', 'producto']),
            models.Index(fields=['mercado']),
        ]
        ordering = ['-fecha']
        verbose_name = "Dato de precio"
        verbose_name_plural = "Datos de precios"

    def __str__(self):
        return f"{self.fecha} - {self.producto.nombre} - {self.region.nombre}"
