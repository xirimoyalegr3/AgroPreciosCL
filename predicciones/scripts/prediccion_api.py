# predicciones/scripts/prediccion_api.py 
import os
import joblib
import unicodedata

def normalizar(texto):
    # Quitar tildes
    texto = ''.join(
        c for c in unicodedata.normalize('NFD', texto)
        if unicodedata.category(c) != 'Mn'
    )
    # Reemplazar espacios por guiones bajos
    texto = texto.replace(" ", "_")
    return texto

def cargar_modelo(fruta, categoria_unidad, region):
    """
    Carga el modelo correspondiente según fruta, categoría y región.
    """
    import inspect
    print("📌 Archivo REAL desde el que se ejecuta cargar_modelo:", inspect.getfile(cargar_modelo))

    # NORMALIZAR AQUÍ
    fruta_norm = normalizar(fruta)
    categoria_norm = normalizar(categoria_unidad)
    region_norm = normalizar(region)

    nombre_modelo = f"{fruta_norm}_{categoria_norm}_{region_norm}_retrained.joblib"

    base_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'models')
    ruta_modelo = os.path.abspath(os.path.join(base_dir, nombre_modelo))

    # DEBUG
    print("🔎 Buscando modelo con nombre:", nombre_modelo)
    print("📍 Ruta completa:", ruta_modelo)
    print("📂 Existe?:", os.path.exists(ruta_modelo))

    if not os.path.exists(ruta_modelo):
        raise FileNotFoundError(f"Modelo no encontrado: {ruta_modelo}")

    modelo = joblib.load(ruta_modelo)
    print(f"✅ Modelo cargado: {ruta_modelo}")
    return modelo
