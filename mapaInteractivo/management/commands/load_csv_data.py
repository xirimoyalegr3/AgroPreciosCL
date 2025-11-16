import os
import json
import pandas as pd
from django.core.management.base import BaseCommand
from mapaInteractivo.models import (Region, Mercado, Subsector, Producto, 
                                   Variedad, DatosComercializacion)
from datetime import datetime
import decimal
from django.db import transaction

class Command(BaseCommand):
    help = 'Carga masiva optimizada desde CSVs, con progreso y control de duplicados'

    def add_arguments(self, parser):
        parser.add_argument('--ruta', type=str, default='datos/', help='Carpeta con los CSV')

    def handle(self, *args, **options):
        ruta_carpeta = options['ruta']
        progreso_path = os.path.join(ruta_carpeta, 'progreso_carga.json')
        progreso = self.cargar_progreso(progreso_path)

        archivos_csv = [a for a in os.listdir(ruta_carpeta) if a.endswith('.csv')]
        if not archivos_csv:
            self.stdout.write(self.style.WARNING('No hay archivos CSV'))
            return

        for archivo in archivos_csv:
            ruta_completa = os.path.join(ruta_carpeta, archivo)
            if not os.path.exists(ruta_completa):
                continue

            chunk_actual = progreso.get(archivo, 0)
            self.stdout.write(f'Procesando {archivo} desde chunk {chunk_actual}...')
            self.cargar_en_chunks(ruta_completa, archivo, progreso_path, progreso, chunk_actual)

        self.stdout.write(self.style.SUCCESS('✅ Carga completa.'))

    # ----------------------------------------------------------------------

    def cargar_en_chunks(self, ruta_archivo, nombre_archivo, progreso_path, progreso, chunk_inicio=0):
        chunk_size = 50000  # número de filas por bloque
        chunk_iter = pd.read_csv(ruta_archivo, encoding='UTF-8-SIG', delimiter=',', chunksize=chunk_size)
        
        # Cache de datos existentes
        regiones_cache = {r.id_region: r for r in Region.objects.all()}
        mercados_cache = {}
        subsectores_cache = {}
        productos_cache = {}
        variedades_cache = {}

        for i, df in enumerate(chunk_iter):
            if i < chunk_inicio:
                continue  # saltar chunks ya procesados

            self.stdout.write(f'🧩 Chunk {i} procesando...')
            
            # Limpiar nombres de columnas
            df.columns = [c.strip().replace('\ufeff', '') for c in df.columns]
            df = self.limpiar_datos(df)

            nuevos_registros = []
            for _, row in df.iterrows():
                try:
                    # Validar datos esenciales
                    if (pd.isna(row.get('ID region')) or pd.isna(row.get('Producto')) or 
                        pd.isna(row.get('Subsector'))):
                        continue

                    # Obtener o crear Region en cache
                    id_region = int(row['ID region'])
                    region_nombre = row['Region']
                    region = regiones_cache.get(id_region)
                    if not region:
                        region, created = Region.objects.get_or_create(
                            id_region=id_region,
                            defaults={'nombre': region_nombre}
                        )
                        regiones_cache[id_region] = region

                    # Obtener o crear Mercado
                    mercado_nombre = row['Mercado']
                    if mercado_nombre not in mercados_cache:
                        mercado, _ = Mercado.objects.get_or_create(nombre=mercado_nombre)
                        mercados_cache[mercado_nombre] = mercado
                    else:
                        mercado = mercados_cache[mercado_nombre]

                    # Obtener o crear Subsector
                    subsector_nombre = row['Subsector']
                    if subsector_nombre not in subsectores_cache:
                        subsector, _ = Subsector.objects.get_or_create(nombre=subsector_nombre)
                        subsectores_cache[subsector_nombre] = subsector
                    else:
                        subsector = subsectores_cache[subsector_nombre]

                    # Obtener o crear Producto (con subsector)
                    producto_nombre = row['Producto']
                    key_producto = (producto_nombre, subsector.id)
                    if key_producto not in productos_cache:
                        producto, _ = Producto.objects.get_or_create(
                            nombre=producto_nombre,
                            subsector=subsector
                        )
                        productos_cache[key_producto] = producto
                    else:
                        producto = productos_cache[key_producto]

                    # Obtener o crear Variedad (puede ser null/blank)
                    variedad_nombre = row['Variedad / Tipo']
                    if pd.isna(variedad_nombre) or variedad_nombre == '':
                        variedad = None
                    else:
                        key_variedad = (variedad_nombre, producto.id)
                        if key_variedad not in variedades_cache:
                            variedad, _ = Variedad.objects.get_or_create(
                                nombre=variedad_nombre,
                                producto=producto
                            )
                            variedades_cache[key_variedad] = variedad
                        else:
                            variedad = variedades_cache[key_variedad]

                    # Fecha segura
                    try:
                        fecha = datetime.strptime(str(row['Fecha']), '%Y-%m-%d').date()
                    except Exception:
                        continue

                    # Crear instancia de DatosComercializacion
                    nuevos_registros.append(
                        DatosComercializacion(
                            fecha=fecha,
                            region=region,
                            mercado=mercado,
                            subsector=subsector,
                            producto=producto,
                            variedad=variedad,
                            calidad=row['Calidad'],
                            unidad_comercializacion=row['Unidad de comercializacion'],
                            origen=row['Origen'],
                            volumen=decimal.Decimal(str(row['Volumen'])),
                            precio_minimo=decimal.Decimal(str(row['Precio minimo'])),
                            precio_maximo=decimal.Decimal(str(row['Precio maximo'])),
                            precio_promedio=decimal.Decimal(str(row['Precio promedio']))
                        )
                    )

                except Exception as e:
                    # Solo mostrar error si es crítico, omitir en grandes volúmenes
                    if "decimal" in str(e).lower():
                        self.stdout.write(f"⚠️ Error decimal en fila: {e}")
                    continue

            # Guardar por bloques en DB
            try:
                with transaction.atomic():
                    DatosComercializacion.objects.bulk_create(
                        nuevos_registros, batch_size=10000, ignore_conflicts=True
                    )
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error guardando chunk {i}: {e}'))

            # Guardar progreso
            progreso[nombre_archivo] = i + 1
            self.guardar_progreso(progreso_path, progreso)
            self.stdout.write(self.style.SUCCESS(f'Chunk {i} completado ({len(nuevos_registros)} registros).'))

    # ----------------------------------------------------------------------

    def limpiar_datos(self, df):
        # Limpiar columnas numéricas (manejar comas como decimales)
        numeric_columns = ['Volumen', 'Precio minimo', 'Precio maximo', 'Precio promedio']
        for col in numeric_columns:
            if col in df.columns:
                # Convertir a string, reemplazar comas por puntos, y luego a numérico
                df[col] = df[col].astype(str)
                df[col] = df[col].str.replace('.', '', regex=False)  # Remover puntos de miles
                df[col] = df[col].str.replace(',', '.', regex=False)  # Coma a punto decimal
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

        # Limpiar columnas de texto
        text_columns = ['Region', 'Mercado', 'Subsector', 'Producto', 'Variedad / Tipo', 
                       'Calidad', 'Unidad de comercializacion', 'Origen']
        for col in text_columns:
            if col in df.columns:
                df[col] = df[col].astype(str).str.strip().fillna('')

        return df

    # ----------------------------------------------------------------------

    def cargar_progreso(self, ruta):
        if os.path.exists(ruta):
            with open(ruta, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}

    def guardar_progreso(self, ruta, data):
        with open(ruta, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)