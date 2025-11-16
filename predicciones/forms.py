# predicciones/forms.py - VERSIÓN CORREGIDA CON SELECT2
from django import forms
from django_select2 import forms as s2forms
from .models import PrecioProducto

class ProductoWidget(s2forms.Select2Widget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Obtener todas las opciones de productos
        productos = PrecioProducto.objects.values_list('producto', 'producto').distinct().order_by('producto')
        self.choices = [('', 'Seleccione producto')] + list(productos)

class RegionWidget(s2forms.Select2Widget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Obtener todas las opciones de regiones
        regiones = PrecioProducto.objects.values_list('region', 'region').distinct().order_by('region')
        self.choices = [('', 'Seleccione región')] + list(regiones)

class PrediccionForm(forms.Form):
    fruta = forms.ChoiceField(
        label="Producto",
        choices=[],  # Se llenará en __init__
        widget=ProductoWidget(attrs={
            'data-placeholder': 'Buscar producto...',
            'class': 'form-control'
        })
    )
    
    categoria = forms.ChoiceField(
        label="Categoría / Unidad",
        choices=[],  # Se llenará en __init__
        widget=forms.Select(attrs={
            'class': 'form-control',
            'id': 'categoria'
        })
    )
    
    region = forms.ChoiceField(
        label="Región",
        choices=[],  # Se llenará en __init__
        widget=RegionWidget(attrs={
            'data-placeholder': 'Buscar región...',
            'class': 'form-control'
        })
    )
    
    horizonte = forms.ChoiceField(
        label="Horizonte de predicción",
        choices=[
            ('1w', '1 semana'),
            ('4w', '4 semanas'),
            ('16w', '16 semanas (4 meses)')
        ],
        widget=forms.Select(attrs={
            'class': 'form-control',
            'id': 'horizonte'
        })
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Llenar opciones para todos los campos
        productos = PrecioProducto.objects.values_list('producto', 'producto').distinct().order_by('producto')
        categorias = PrecioProducto.objects.values_list('categoria_unidad', 'categoria_unidad').distinct().order_by('categoria_unidad')
        regiones = PrecioProducto.objects.values_list('region', 'region').distinct().order_by('region')
        
        self.fields['fruta'].choices = [('', '--- Seleccione Producto ---')] + list(productos)
        self.fields['categoria'].choices = [('', '--- Seleccione Categoría ---')] + list(categorias)
        self.fields['region'].choices = [('', '--- Seleccione Región ---')] + list(regiones)