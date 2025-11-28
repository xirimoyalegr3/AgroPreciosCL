import os
import unicodedata
from django.conf import settings

def normalize(s):
    s = unicodedata.normalize('NFKD', s).encode('ascii', 'ignore').decode('ascii')
    s = s.replace(" ", "_").replace("-", "_")
    return s

def normalizar_nombres_modelos():
    model_dir = os.path.join(settings.BASE_DIR, "modelos")

    print("Carpeta modelos:", model_dir)

    archivos = os.listdir(model_dir)
    print("Archivos encontrados:", archivos)

    for archivo in archivos:
        ruta_actual = os.path.join(model_dir, archivo)

        nombre, ext = os.path.splitext(archivo)

        nombre_normalizado = normalize(nombre)

        nuevo_nombre = nombre_normalizado + ext
        nueva_ruta = os.path.join(model_dir, nuevo_nombre)

        if archivo == nuevo_nombre:
            print(f"Sin cambios: {archivo}")
            continue

        print(f"Renombrando: {archivo}  →  {nuevo_nombre}")
        os.rename(ruta_actual, nueva_ruta)

    print("Normalización completa.")
