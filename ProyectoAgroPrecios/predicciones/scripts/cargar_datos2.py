import os
import pandas as pd
from django.conf import settings
from predicciones.models import PrecioProducto

def cargar_datos_desde_csv(nombre_archivo="datos_combinados_features_2016-2025.csv"):
    ruta_csv = os.path.join(settings.BASE_DIR, "datos", nombre_archivo)
    print(f"📥 Cargando datos desde: {ruta_csv}")

    df = pd.read_csv(ruta_csv)

    print(f"📊 Columnas encontradas: {list(df.columns)}")
    print(f"📈 Total de filas: {len(df)}")

    objetos = []
    for _, row in df.iterrows():
        try:
            objetos.append(PrecioProducto(
                producto=row.get('producto'),
                unidad_de_comercializacion=row.get('unidad_de_comercializacion'),
                categoria_unidad=row.get('categoria_unidad'),
                producto_unidad=row.get('producto_unidad'),
                region=row.get('region'),
                mercado=row.get('mercado'),
                fecha=pd.to_datetime(row.get('fecha')).date(),
                volumen=row.get('volumen'),
                precio_minimo=row.get('precio_minimo'),
                precio_maximo=row.get('precio_maximo'),
                precio_promedio=row.get('precio_promedio'),
                precio_normalizado=row.get('precio_normalizado'),
                factor_inferido=row.get('factor_inferido'),
                calidad=row.get('calidad'),
                origen=row.get('origen'),
            ))
        except Exception as e:
            print(f"⚠️ Error al procesar fila: {e}")
            continue

        # Guardar por lotes cada 5000 filas para no saturar la memoria
        if len(objetos) >= 5000:
            PrecioProducto.objects.bulk_create(objetos, ignore_conflicts=True)
            objetos.clear()
            print("💾 Guardado parcial de 5000 registros")

    # Guardar los que queden
    if objetos:
        PrecioProducto.objects.bulk_create(objetos, ignore_conflicts=True)
        print(f"💾 Guardado final de {len(objetos)} registros")

    print("✅ Carga completa de datos en la base de datos")
