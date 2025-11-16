# predicciones/views.py - VERSIÓN COMPLETA CORREGIDA
from django.shortcuts import render
from django.core.cache import cache
from predicciones.models import PrecioProducto
from predicciones.scripts.prediccion_api import cargar_modelo
from predicciones.forms import PrediccionForm
from predicciones.utils import calcular_metricas_confianza, obtener_datos_historicos_para_validacion
import pandas as pd
import numpy as np
from datetime import timedelta, datetime
import json

def prediccion_home(request):
    """
    Vista principal para realizar predicciones de precios
    """
    if request.method == 'POST':
        form = PrediccionForm(request.POST)
        
        if form.is_valid():
            # Obtener datos del formulario
            fruta = form.cleaned_data['fruta']
            unidad = form.cleaned_data['categoria']
            region = form.cleaned_data['region']
            horizonte = form.cleaned_data['horizonte']
            
            print(f"🎯 Iniciando predicción: {fruta} - {unidad} - {region} - {horizonte}")
            
            # 🔹 VERIFICAR CACHE PRIMERO (sin incluir el form)
            cache_key = f"prediccion_{fruta}_{region}_{unidad}_{horizonte}"
            cached_result = cache.get(cache_key)
            
            if cached_result:
                print("✅ Usando predicción desde cache")
                # Crear un nuevo form para mostrar (no usar el del cache)
                categorias = PrecioProducto.objects.values_list('categoria_unidad', flat=True).distinct()
                form.fields['categoria'].choices = [(c, c) for c in categorias]
                cached_result['form'] = form  # Agregar el form actual
                return render(request, 'predicciones/prediccion_resultado.html', cached_result)
            
            try:
                # 🔹 CARGAR MODELO
                modelo = cargar_modelo(fruta, unidad, region)
                print("✅ Modelo cargado correctamente")
                
            except FileNotFoundError:
                print("❌ Modelo no encontrado")
                categorias = PrecioProducto.objects.values_list('categoria_unidad', flat=True).distinct()
                form.fields['categoria'].choices = [(c, c) for c in categorias]
                return render(request, 'predicciones/home.html', {
                    'form': form,
                    'error': 'No se encontró modelo entrenado para esta combinación de producto, región y unidad.'
                })
            except Exception as e:
                print(f"❌ Error cargando modelo: {e}")
                categorias = PrecioProducto.objects.values_list('categoria_unidad', flat=True).distinct()
                form.fields['categoria'].choices = [(c, c) for c in categorias]
                return render(request, 'predicciones/home.html', {
                    'form': form,
                    'error': f'Error al cargar el modelo: {str(e)}'
                })

            # 🔹 OBTENER DATOS HISTÓRICOS
            registros = PrecioProducto.objects.filter(
                producto=fruta,
                region=region,
                categoria_unidad=unidad
            ).order_by('-fecha')[:90]

            df = pd.DataFrame(list(registros.values()))
            
            # 🔹 OBTENER ÚLTIMO DATO REAL Y CALCULAR FECHAS
            ultimo_dato_real = None
            precio_ultimo_real = None
            fecha_ultimo_real = None
            campo_usado = 'precio_normalizado'
            ultima_fecha_datos = None

            if not df.empty:
                df['fecha'] = pd.to_datetime(df['fecha'])
                df = df.sort_values('fecha')
                
                # Buscar el registro más reciente que tenga precio_normalizado
                ultimo_registro = df[df['precio_normalizado'].notna()].tail(1)
                
                if not ultimo_registro.empty:
                    ultimo_dato_real = ultimo_registro.iloc[0]
                    precio_ultimo_real = ultimo_dato_real['precio_normalizado']
                    fecha_ultimo_real = ultimo_dato_real['fecha'].strftime('%Y-%m-%d')
                    ultima_fecha_datos = ultimo_dato_real['fecha'].date()
                    print(f"📊 Último dato real: {fecha_ultimo_real} - ${precio_ultimo_real}")
                else:
                    # Fallback a precio_promedio si no hay precio_normalizado
                    ultimo_registro = df[df['precio_promedio'].notna()].tail(1)
                    if not ultimo_registro.empty:
                        ultimo_dato_real = ultimo_registro.iloc[0]
                        precio_ultimo_real = ultimo_dato_real['precio_promedio']
                        fecha_ultimo_real = ultimo_dato_real['fecha'].strftime('%Y-%m-%d')
                        ultima_fecha_datos = ultimo_dato_real['fecha'].date()
                        campo_usado = 'precio_promedio'
                        print(f"📊 Último dato real (promedio): {fecha_ultimo_real} - ${precio_ultimo_real}")
                    else:
                        print("⚠️ No se encontraron datos reales con precio_normalizado ni precio_promedio")
                        # Si no hay datos válidos, usar la fecha más reciente del dataset
                        ultima_fecha_datos = df['fecha'].max().date() if not df.empty else datetime.now().date()
            else:
                ultima_fecha_datos = datetime.now().date()
                print("⚠️ No hay datos históricos")

            # 🔹 CALCULAR FECHAS DE PREDICCIÓN BASADAS EN ÚLTIMO DATO DISPONIBLE
            print(f"📊 Última fecha en datos: {ultima_fecha_datos}")

            # Calcular el próximo ciclo (lunes) después del último dato disponible
            dias_hasta_proximo_ciclo = (0 - ultima_fecha_datos.weekday()) % 7
            if dias_hasta_proximo_ciclo == 0:
                # Si el último dato es lunes, usar el próximo lunes
                dias_hasta_proximo_ciclo = 7

            fecha_inicio_prediccion = ultima_fecha_datos + timedelta(days=dias_hasta_proximo_ciclo)

            print(f"🎯 Inicio predicción (próximo ciclo ODEPA): {fecha_inicio_prediccion}")

            # 🔹 CALCULAR DÍAS SIN DATOS
            dias_sin_datos = None
            if not df.empty:
                dias_sin_datos = (fecha_inicio_prediccion - ultima_fecha_datos).days - 7
                if dias_sin_datos < 0:
                    dias_sin_datos = 0
                print(f"📅 Días sin datos antes de predicción: {dias_sin_datos} días")

            if df.empty:
                # Si no hay datos históricos
                print("⚠️ No hay datos históricos, usando valores base")
                X_actual = pd.DataFrame([{
                    'mes': fecha_inicio_prediccion.month, 
                    'ano': fecha_inicio_prediccion.year, 
                    'dia_semana': 0,
                    'es_fin_de_semana': 0,
                    'lag_1': 1000, 'lag_7': 1000, 'lag_30': 1000,
                    'rol_mean_7': 1000, 'rol_std_30': 100, 'pct_change_7': 0
                }])
            else:
                # 🔹 PARA EL MODELO: Usar precio_normalizado como campo principal
                campo_precio_modelo = 'precio_normalizado'
                
                # Si no hay precio_normalizado, usar precio_promedio como fallback
                if df['precio_normalizado'].isna().all() and not df['precio_promedio'].isna().all():
                    campo_precio_modelo = 'precio_promedio'
                    print("⚠️ Usando precio_promedio como fallback para el modelo")
                elif df['precio_normalizado'].isna().all():
                    # Si ambos están vacíos, crear valores dummy
                    df['precio_normalizado'] = df.get('precio_minimo', 1000)
                    print("⚠️ Usando valores dummy para precio_normalizado")
                
                print(f"🎯 Campo usado para el modelo: {campo_precio_modelo}")
                
                # Calcular características temporales para el modelo
                df['mes'] = df['fecha'].dt.month
                df['ano'] = df['fecha'].dt.year
                df['dia_semana'] = df['fecha'].dt.weekday
                df['es_fin_de_semana'] = df['dia_semana'].isin([5, 6]).astype(int)
                
                precio_series = df[campo_precio_modelo].fillna(method='ffill').fillna(method='bfill')
                
                df['lag_1'] = precio_series.shift(1)
                df['lag_7'] = precio_series.shift(7)
                df['lag_30'] = precio_series.shift(30)
                df['rol_mean_7'] = precio_series.rolling(7, min_periods=1).mean()
                df['rol_std_30'] = precio_series.rolling(30, min_periods=1).std()
                df['pct_change_7'] = precio_series.pct_change(7)
                
                df = df.fillna(0)
                
                # Tomar la última fila para predicción
                columnas_modelo = ['mes', 'ano', 'dia_semana', 'es_fin_de_semana',
                                  'lag_1', 'lag_7', 'lag_30', 'rol_mean_7', 'rol_std_30', 'pct_change_7']
                
                for col in columnas_modelo:
                    if col not in df.columns:
                        df[col] = 0
                
                X_actual = df[columnas_modelo].tail(1)
                print(f"📊 Última fecha en datos históricos: {df['fecha'].max()}")
                print(f"🎯 Características para predicción: {X_actual.to_dict('records')[0]}")

            # 🔹 PREDICCIÓN SEMANAL
            if horizonte == '1w':
                semanas = 1
            elif horizonte == '4w':
                semanas = 4
            else:  # '16w'
                semanas = 16
            
            fechas_prediccion = [fecha_inicio_prediccion + timedelta(weeks=i) for i in range(semanas)]
            precios_predichos = []
            
            X_pred = X_actual.copy()

            print("🔮 Iniciando predicción iterativa...")
            for i in range(semanas):
                try:
                    fecha_pred = fecha_inicio_prediccion + timedelta(weeks=i)
                    
                    X_pred['mes'] = fecha_pred.month
                    X_pred['ano'] = fecha_pred.year
                    X_pred['dia_semana'] = 0
                    X_pred['es_fin_de_semana'] = 0
                    
                    y_pred = modelo.predict(X_pred)[0]
                    precios_predichos.append(float(y_pred))
                    
                    # Actualizar para siguiente predicción
                    X_pred['lag_1'] = y_pred
                    X_pred['lag_7'] = precios_predichos[-1] if precios_predichos else y_pred
                    X_pred['lag_30'] = precios_predichos[-1] if precios_predichos else y_pred
                    
                    ventana_4 = precios_predichos[-4:] if len(precios_predichos) >= 4 else precios_predichos
                    X_pred['rol_mean_7'] = np.mean(ventana_4)
                    
                    ventana_12 = precios_predichos[-12:] if len(precios_predichos) >= 12 else precios_predichos
                    X_pred['rol_std_30'] = np.std(ventana_12) if len(ventana_12) > 1 else 0
                    
                    if len(precios_predichos) >= 2:
                        X_pred['pct_change_7'] = (precios_predichos[-1] - precios_predichos[-2]) / precios_predichos[-2]
                    else:
                        X_pred['pct_change_7'] = 0
                        
                    print(f"📅 Semana {i+1}: {fecha_pred} - Precio: ${y_pred:.2f}")
                        
                except Exception as e:
                    print(f"❌ Error en predicción semana {i+1}: {e}")
                    # En caso de error, usar el último precio predicho o un valor base
                    ultimo_precio = precios_predichos[-1] if precios_predichos else 1000
                    precios_predichos.append(ultimo_precio)

            #CALCULAR MÉTRICAS DE CONFIANZA
            print("Calculando métricas de confianza...")
            precios_historicos = obtener_datos_historicos_para_validacion(fruta, region, unidad)

            if len(precios_historicos) >= 5 and len(precios_predichos) >= 5:
                metricas = calcular_metricas_confianza(precios_historicos, precios_predichos)
                print(f"✅ Métricas calculadas: {metricas['confianza']}% de confianza")
                print(f"📈 Tendencia: {metricas['tendencia']}")
                print(f"⚡ Volatilidad: {metricas['volatilidad']}")
            else:
                metricas = {
                    'confianza': 75, 
                    'tendencia': 'estable', 
                    'volatilidad': 'media', 
                    'rmse': 0, 
                    'mae': 0,
                    'error_relativo': 0
                }
                print("Métricas base por datos insuficientes")
            # 🔹 PREPARAR DATOS PARA EL GRÁFICO CON ÚLTIMO DATO REAL
            datos_grafico = {
                'predicciones': [],
                'ultimo_real': None
            }

            # Agregar último dato real si existe
            if ultimo_dato_real is not None:
                precio_mostrar = ultimo_dato_real.get('precio_normalizado')
                if precio_mostrar is None or np.isnan(precio_mostrar):
                    precio_mostrar = ultimo_dato_real.get('precio_promedio')
                
                datos_grafico['ultimo_real'] = {
                    'fecha': fecha_ultimo_real,
                    'precio': float(precio_mostrar) if precio_mostrar is not None else 0,
                    'tipo': 'real',
                    'campo_usado': campo_usado
                }

            # Agregar predicciones
            for fecha, precio in zip(fechas_prediccion, precios_predichos):
                datos_grafico['predicciones'].append({
                    'fecha': fecha.strftime('%Y-%m-%d'),
                    'precio': round(precio, 2),
                    'tipo': 'prediccion',
                    'semana': f"Semana {(fecha - fecha_inicio_prediccion).days // 7 + 1}"
                })

            # Resultados para la tabla (solo predicciones)
            resultados_tabla = []
            for fecha, precio in zip(fechas_prediccion, precios_predichos):
                resultados_tabla.append({
                    'fecha': fecha.strftime('%Y-%m-%d'),
                    'precio_predicho': round(precio, 2),
                    'semana': f"Semana {(fecha - fecha_inicio_prediccion).days // 7 + 1}"
                })

            # Preparar contexto para el último dato real
            ultimo_dato_real_context = None
            if ultimo_dato_real is not None:
                ultimo_dato_real_context = {
                    'fecha': fecha_ultimo_real,
                    'precio': precio_ultimo_real,
                    'campo_usado': campo_usado
                }

            # 🔹 PREPARAR CONTEXTO FINAL (SIN EL FORM PARA CACHE)
            cache_context = {
                'fruta': fruta,
                'region': region,
                'unidad': unidad,
                'horizonte': horizonte,
                'resultados': resultados_tabla,
                'datos_grafico_json': json.dumps(datos_grafico),
                'proximo_lunes': fecha_inicio_prediccion.strftime('%Y-%m-%d'),
                'ultimo_dato_real': ultimo_dato_real_context,
                'metricas': metricas,
                'dias_sin_datos': dias_sin_datos,
                'ultima_fecha_datos': ultima_fecha_datos.strftime('%Y-%m-%d') if ultima_fecha_datos else None
            }

            # Contexto para renderizar (SÍ incluye el form)
            render_context = cache_context.copy()
            render_context['form'] = form

            # 🔹 GUARDAR EN CACHE (solo datos serializables)
            cache.set(cache_key, cache_context, 3600)  # Cache por 1 hora
            print(f"💾 Predicción guardada en cache (key: {cache_key})")
            print(f"✅ Predicción completada: {len(precios_predichos)} semanas")
            print(f"📅 Rango de fechas: {fechas_prediccion[0]} a {fechas_prediccion[-1]}")
            print(f"📊 Rango de precios predichos: ${min(precios_predichos):.2f} - ${max(precios_predichos):.2f}")

            return render(request, 'predicciones/prediccion_resultado.html', render_context)
        else:
            # Formulario no válido
            print("❌ Formulario no válido")
            categorias = PrecioProducto.objects.values_list('categoria_unidad', flat=True).distinct()
            form.fields['categoria'].choices = [(c, c) for c in categorias]
            return render(request, 'predicciones/home.html', {
                'form': form,
                'error': 'Por favor, complete todos los campos correctamente.'
            })
    
    else:
        # GET request - mostrar formulario vacío
        form = PrediccionForm()
        # Llenar opciones de categoría
        categorias = PrecioProducto.objects.values_list('categoria_unidad', flat=True).distinct()
        form.fields['categoria'].choices = [(c, c) for c in categorias]
        
        return render(request, 'predicciones/home.html', {
            'form': form
        })


def prediccion_resultado(request):
    """
    Vista auxiliar para mostrar resultados (si se accede directamente)
    """
    return render(request, 'predicciones/prediccion_resultado.html')


def limpiar_cache(request):
    """
    Vista para limpiar el cache (útil para desarrollo)
    """
    if request.user.is_superuser:
        cache.clear()
        return render(request, 'predicciones/home.html', {
            'form': PrediccionForm(),
            'success': '✅ Cache limpiado correctamente'
        })
    else:
        return render(request, 'predicciones/home.html', {
            'form': PrediccionForm(),
            'error': 'No tiene permisos para realizar esta acción'
        })