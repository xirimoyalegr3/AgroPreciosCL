# predicciones/scripts/prediccion_api.py
import os
import joblib

def cargar_modelo(fruta, categoria_unidad, region):
    """
    Carga el modelo correspondiente según fruta, categoría y región.
    """
    base_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'models')

    # Asegurar que los nombres de archivo coincidan con el formato exacto
    nombre_modelo = f"{fruta}_{categoria_unidad}_{region}_retrained.joblib"

    ruta_modelo = os.path.join(base_dir, nombre_modelo)

    # Normalizar espacios y acentos (opcional)
    ruta_modelo = ruta_modelo.replace(" ", "_")

    if not os.path.exists(ruta_modelo):
        raise FileNotFoundError(f"Modelo no encontrado: {ruta_modelo}")

    modelo = joblib.load(ruta_modelo)
    print(f"✅ Modelo cargado: {ruta_modelo}")
    return modelo
