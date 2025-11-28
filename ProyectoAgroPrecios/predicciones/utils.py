# predicciones/utils.py - VERSIÓN CORREGIDA
import numpy as np
from sklearn.metrics import mean_squared_error, mean_absolute_error

def calcular_metricas_confianza(precios_historicos, precios_predichos):
    """
    Calcular métricas de confianza para las predicciones
    """
    if len(precios_historicos) < 5 or len(precios_predichos) < 5:
        return {
            'confianza': 75,
            'rmse': 0,
            'mae': 0,
            'tendencia': 'estable',
            'volatilidad': 'media',
            'error_relativo': 0
        }
    
    try:
        # Usar los últimos datos históricos para validación
        min_len = min(len(precios_historicos), len(precios_predichos))
        y_true = precios_historicos[-min_len:]
        y_pred = precios_predichos[:min_len]
        
        # Calcular errores
        rmse = np.sqrt(mean_squared_error(y_true, y_pred))
        mae = mean_absolute_error(y_true, y_pred)
        
        # Calcular confianza basada en error relativo
        mean_true = np.mean(y_true)
        if mean_true == 0:
            error_relativo = 1
        else:
            error_relativo = rmse / mean_true
        
        # Convertir a porcentaje de confianza (0-100%)
        # Mientras menor el error relativo, mayor la confianza
        confianza = max(0, min(100, 100 - (error_relativo * 100)))
        
        # Determinar tendencia basada en las predicciones
        if len(precios_predichos) >= 2:
            # Calcular tendencia de las predicciones futuras
            primer_precio = precios_predichos[0]
            ultimo_precio = precios_predichos[-1]
            cambio_porcentual = ((ultimo_precio - primer_precio) / primer_precio) * 100
            
            if cambio_porcentual > 5:
                tendencia = 'ascendente'
            elif cambio_porcentual < -5:
                tendencia = 'descendente'
            else:
                tendencia = 'estable'
        else:
            tendencia = 'estable'
        
        # Determinar volatilidad de las predicciones
        if len(precios_predichos) >= 2:
            volatilidad_val = np.std(precios_predichos) / np.mean(precios_predichos) if np.mean(precios_predichos) != 0 else 0
            if volatilidad_val < 0.05:  # 5% de volatilidad
                volatilidad = 'baja'
            elif volatilidad_val < 0.15:  # 15% de volatilidad
                volatilidad = 'media'
            else:
                volatilidad = 'alta'
        else:
            volatilidad = 'media'
        
        return {
            'confianza': round(confianza),
            'rmse': round(rmse, 2),
            'mae': round(mae, 2),
            'tendencia': tendencia,
            'volatilidad': volatilidad,
            'error_relativo': round(error_relativo * 100, 2),
            'cambio_porcentual': round(cambio_porcentual, 2) if 'cambio_porcentual' in locals() else 0
        }
        
    except Exception as e:
        print(f"❌ Error calculando métricas: {e}")
        return {
            'confianza': 70,
            'rmse': 0,
            'mae': 0,
            'tendencia': 'estable',
            'volatilidad': 'media',
            'error_relativo': 0
        }

def obtener_datos_historicos_para_validacion(fruta, region, unidad, dias=60):
    """
    Obtener datos históricos para validar el modelo
    """
    from .models import PrecioProducto
    from datetime import datetime, timedelta
    
    fecha_fin = datetime.now().date()
    fecha_inicio = fecha_fin - timedelta(days=dias)
    
    datos = PrecioProducto.objects.filter(
        producto=fruta,
        region=region,
        categoria_unidad=unidad,
        fecha__range=[fecha_inicio, fecha_fin]
    ).order_by('fecha')
    
    # Extraer precios normalizados (no nulos)
    precios = []
    for dato in datos:
        if dato.precio_normalizado is not None:
            precios.append(float(dato.precio_normalizado))
        elif dato.precio_promedio is not None:
            precios.append(float(dato.precio_promedio))
    
    return precios