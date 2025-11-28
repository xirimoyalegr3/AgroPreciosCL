# predicciones/models.py
from django.db import models

class PrecioProducto(models.Model):
    producto = models.CharField(max_length=100, db_index=True)
    unidad_de_comercializacion = models.CharField(max_length=80, blank=True, null=True)
    categoria_unidad = models.CharField(max_length=50, blank=True, null=True, db_index=True)
    producto_unidad = models.CharField(max_length=150, db_index=True)  # ej: "Papa (por_kilo)"
    region = models.CharField(max_length=120, db_index=True)
    mercado = models.CharField(max_length=150, blank=True, null=True)   # opcional
    fecha = models.DateField(db_index=True)
    volumen = models.FloatField(blank=True, null=True)

    precio_minimo = models.FloatField(blank=True, null=True)
    precio_maximo = models.FloatField(blank=True, null=True)
    precio_promedio = models.FloatField(blank=True, null=True)
    precio_normalizado = models.FloatField(blank=True, null=True, db_index=True)
    factor_inferido = models.FloatField(blank=True, null=True)

    calidad = models.CharField(max_length=80, blank=True, null=True)
    origen = models.CharField(max_length=120, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Precio Producto"
        verbose_name_plural = "Precios Productos"
        unique_together = (
            (
                'producto_unidad',
                'region',
                'fecha',
                'mercado',
                'unidad_de_comercializacion',
                'calidad',
            ),
        )


    def __str__(self):
        return f"{self.producto_unidad} | {self.region} | {self.fecha}"


# Create your models here.
