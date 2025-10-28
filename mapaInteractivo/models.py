# mapaInteractivo/models.py 
from django.db import models

class Region(models.Model):
    id_region = models.IntegerField(unique=True)
    nombre = models.CharField(max_length=100)
    
    def __str__(self):
        return self.nombre

class Mercado(models.Model):
    nombre = models.CharField(max_length=200)
    
    def __str__(self):
        return self.nombre

class Subsector(models.Model):
    nombre = models.CharField(max_length=100)
    
    def __str__(self):
        return self.nombre

class Producto(models.Model):
    nombre = models.CharField(max_length=100)
    subsector = models.ForeignKey(Subsector, on_delete=models.CASCADE)
    
    def __str__(self):
        return self.nombre

class Variedad(models.Model):
    nombre = models.CharField(max_length=100)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    
    def __str__(self):
        return self.nombre

class DatosComercializacion(models.Model):
    fecha = models.DateField()
    region = models.ForeignKey(Region, on_delete=models.CASCADE)
    mercado = models.ForeignKey(Mercado, on_delete=models.CASCADE)
    subsector = models.ForeignKey(Subsector, on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    variedad = models.ForeignKey(Variedad, on_delete=models.CASCADE, null=True, blank=True)
    calidad = models.CharField(max_length=50)
    unidad_comercializacion = models.CharField(max_length=100)
    origen = models.CharField(max_length=100)
    volumen = models.DecimalField(max_digits=15, decimal_places=2)
    precio_minimo = models.DecimalField(max_digits=15, decimal_places=2)
    precio_maximo = models.DecimalField(max_digits=15, decimal_places=2)
    precio_promedio = models.DecimalField(max_digits=15, decimal_places=2)
    
    class Meta:
        indexes = [
            models.Index(fields=['fecha']),
            models.Index(fields=['region']),
            models.Index(fields=['producto']),
        ]

class ProgresoCarga(models.Model):
    archivo = models.CharField(max_length=255)
    lineas_procesadas = models.IntegerField(default=0)
    total_lineas = models.IntegerField(default=0)
    completado = models.BooleanField(default=False)
    fecha_inicio = models.DateTimeField(auto_now_add=True)
    fecha_fin = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.archivo} - {self.lineas_procesadas}/{self.total_lineas}"
    
    def get_porcentaje(self):
        """Calcula el porcentaje de completado"""
        if self.total_lineas == 0:
            return 0
        return (self.lineas_procesadas / self.total_lineas) * 100

        
    def __str__(self):
        return f"{self.archivo} - {self.lineas_procesadas}/{self.total_lineas}"