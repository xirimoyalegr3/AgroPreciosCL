# predicciones/views.py
from django.shortcuts import render
from predicciones.models import PrecioProducto
from predicciones.scripts.prediccion_api import cargar_modelo
import pandas as pd
import numpy as np
from datetime import timedelta

def prediccion_home(request):
    # 🔹 Cargamos los valores únicos para el formulario
    # Cargar valores únicos para los selects
    productos = PrecioProducto.objects.values_list('producto', flat=True).distinct().order_by('producto')
    regiones = PrecioProducto.objects.values_list('region', flat=True).distinct().order_by('region')
    unidades = PrecioProducto.objects.values_list('categoria_unidad', flat=True).distinct().order_by('categoria_unidad')


    resultados = None

    if request.method == 'POST':
        fruta = request.POST.get('fruta')
        unidad = request.POST.get('categoria')
        region = request.POST.get('region')
        horizonte = request.POST.get('horizonte')

        # 🔹 Cargar el modelo correspondiente
        modelo = cargar_modelo(fruta, unidad, region)

        # 🔹 Obtener los últimos registros para esa combinación
        df = pd.DataFrame(list(
            PrecioProducto.objects.filter(
                producto=fruta,
                region=region,
                categoria_unidad=unidad

            ).order_by('-fecha')[:90].values()
        ))

        if df.empty:
            # Si no hay datos, generar un input ficticio neutro
            X = pd.DataFrame([{
                'mes': 1, 'ano': 2025, 'dia_semana': 0, 'es_fin_de_semana': 0,
                'lag_1': 0, 'lag_7': 0, 'lag_30': 0,
                'rol_mean_7': 0, 'rol_std_30': 0, 'pct_change_7': 0
            }])
            ultima_fecha = pd.Timestamp.today()
        else:
            # 🔹 Generar columnas derivadas igual que en el entrenamiento
            df['fecha'] = pd.to_datetime(df['fecha'])
            df['mes'] = df['fecha'].dt.month
            df['ano'] = df['fecha'].dt.year
            df['dia_semana'] = df['fecha'].dt.weekday
            df['es_fin_de_semana'] = df['dia_semana'].isin([5, 6]).astype(int)

            # Asegurar que existan todas las columnas necesarias
            for col in ['lag_1', 'lag_7', 'lag_30', 'rol_mean_7', 'rol_std_30', 'pct_change_7']:
                if col not in df.columns:
                    df[col] = 0

            ultima_fecha = df['fecha'].max()
            X = df[['mes', 'ano', 'dia_semana', 'es_fin_de_semana',
                    'lag_1', 'lag_7', 'lag_30', 'rol_mean_7', 'rol_std_30', 'pct_change_7']].tail(1)

        # 🔹 Predicción iterativa (día a día)
        dias = 7 if horizonte == '7d' else 28 if horizonte == '4w' else 120
        fechas = [ultima_fecha + timedelta(days=i) for i in range(1, dias + 1)]
        precios = []

        X_actual = X.copy()

        for i in range(dias):
            y_pred = modelo.predict(X_actual)[0]
            precios.append(float(y_pred))

            # Actualizar las variables lag dinámicamente
            X_actual['lag_1'] = y_pred
            X_actual['lag_7'] = X_actual['lag_1']
            X_actual['lag_30'] = X_actual['lag_7']
            X_actual['rol_mean_7'] = np.mean(precios[-7:]) if len(precios) >= 7 else np.mean(precios)
            X_actual['rol_std_30'] = np.std(precios[-30:]) if len(precios) >= 2 else 0
            X_actual['pct_change_7'] = (precios[-1] - precios[0]) / precios[0] if len(precios) > 1 else 0

        resultados = pd.DataFrame({'fecha': fechas, 'precio_predicho': precios})

        # 🔹 Renderizar los resultados
        return render(request, 'predicciones/prediccion_resultado.html', {
            'fruta': fruta,
            'region': region,
            'unidad': unidad,
            'horizonte': horizonte,
            'resultados': resultados.to_dict(orient='records')
        })

    # 🔹 Página principal (formulario)
    return render(request, 'predicciones/home.html', {
        'productos': productos,
        'regiones': regiones,
        'categorias': unidades,
    })


def prediccion_resultado(request):
    """Vista auxiliar (si se entra directo a la plantilla de resultado)."""
    return render(request, 'predicciones/prediccion_resultado.html')