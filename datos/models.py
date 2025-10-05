from django.db import models

class Region(models.Model):
    id_region = models.IntegerField(unique=True)
    nombre = models.CharField(max_length=100)
    
    def __str__(self):
        return self.nombre

class Mercado(models.Model):
    nombre = models.CharField(max_length=200)
    region = models.ForeignKey(Region, on_delete=models.CASCADE)
    
    def __str__(self):
        return self.nombre

class Producto(models.Model):
    subsector = models.CharField(max_length=100)
    nombre = models.CharField(max_length=200)
    variedad_tipo = models.CharField(max_length=100)
    calidad = models.CharField(max_length=50)
    unidad_comercializacion = models.CharField(max_length=100)
    origen = models.CharField(max_length=100)
    
    def __str__(self):
        return f"{self.nombre} - {self.variedad_tipo}"

class PrecioDatos(models.Model):
    fecha = models.DateField()
    region = models.ForeignKey(Region, on_delete=models.CASCADE)
    mercado = models.ForeignKey(Mercado, on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    volumen = models.DecimalField(max_digits=15, decimal_places=2)
    precio_minimo = models.DecimalField(max_digits=12, decimal_places=4)
    precio_maximo = models.DecimalField(max_digits=12, decimal_places=4)
    precio_promedio = models.DecimalField(max_digits=12, decimal_places=4)  # Cambiado de precio_promedio_ponderado
    
    class Meta:
        indexes = [
            models.Index(fields=['fecha']),
            models.Index(fields=['region', 'producto']),
        ]
        verbose_name_plural = "Datos de precios"
    
    def __str__(self):
        return f"{self.fecha} - {self.producto.nombre} - {self.region.nombre}"