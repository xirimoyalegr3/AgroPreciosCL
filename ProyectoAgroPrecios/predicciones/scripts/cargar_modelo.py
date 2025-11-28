# predicciones/scripts/cargar_modelos.py
import os
import unicodedata
import joblib
from django.conf import settings

# Ajusta si tu carpeta se llama "modelos" o "models"
MODEL_DIR = os.path.join(settings.BASE_DIR, "modelos")

def normalize_to_filename(s: str) -> str:
    """
    Normaliza cadenas para nombres de archivo:
    - Quita tildes/diacríticos
    - Reemplaza espacios y guiones por guión bajo
    - Elimina caracteres que puedan molestar
    """
    if not s:
        return ""
    # quitar acentos
    s = unicodedata.normalize('NFKD', str(s)).encode('ascii', 'ignore').decode('ascii')
    # reemplazos seguros
    s = s.replace(" ", "_").replace("-", "_").replace("/", "_").replace("\\", "_")
    # opcional: eliminar comas u otros símbolos
    s = "".join(ch for ch in s if ch.isalnum() or ch == "_")
    return s

def _list_models():
    try:
        return sorted(os.listdir(MODEL_DIR))
    except FileNotFoundError:
        return []

def cargar_modelo(producto: str, categoria: str, region: str):
    """
    Busca y carga un modelo .joblib en MODEL_DIR probando variantes normalizadas.
    Lanza FileNotFoundError si no lo encuentra.
    """
    p = normalize_to_filename(producto)
    c = normalize_to_filename(categoria)
    r = normalize_to_filename(region)

    # variantes a probar (agrega más si los tuyos usan otro sufijo)
    posibles = [
        f"{p}_{c}_{r}_retrained.joblib",
        f"{p}_{c}_{r}.joblib",
        f"{p}_{c}_{r}_model.joblib",
        f"{p}_{r}_{c}_retrained.joblib",
        f"{p}_{c}_{r}_trained.joblib",
    ]

    archivos = _list_models()
    print("🔎 Carpeta de modelos:", MODEL_DIR)
    print("🔎 Modelos disponibles:", archivos)

    # buscar coincidencia exacta ignorando mayúsculas
    for candidato in posibles:
        for archivo in archivos:
            if archivo.lower() == candidato.lower():
                ruta = os.path.join(MODEL_DIR, archivo)
                print("Coincidencia exacta encontrada:", archivo)
                try:
                    return joblib.load(ruta)
                except Exception as e:
                    raise RuntimeError(f"Error cargando modelo '{ruta}': {e}")

    # buscar coincidencias parciales producto+region
    parcial = [f for f in archivos if p.lower() in f.lower() and r.lower() in f.lower()]
    if parcial:
        print("Coincidencias parciales:", parcial)
        for archivo in parcial:
            ruta = os.path.join(MODEL_DIR, archivo)
            try:
                return joblib.load(ruta)
            except Exception as e:
                print(f"Falló carga parcial {ruta}: {e}")

    raise FileNotFoundError(f"No se encontró modelo para {producto}/{categoria}/{region}. Buscados: {posibles}")
