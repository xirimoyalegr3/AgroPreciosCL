import os
import json
import pandas as pd
from django.core.management.base import BaseCommand
from datos.models import Region, Mercado, Producto, PrecioDatos
from datetime import datetime
import decimal
from django.db import transaction

class Command(BaseCommand):
    help = 'Carga masiva optimizada desde CSVs, con progreso y control de duplicados'

    def add_arguments(self, parser):
        parser.add_argument('--ruta', type=str, default='data/', help='Carpeta con los CSV')

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
        
        # Mapeo columnas
        mapeo_columnas = {
            'Fecha': 'fecha',
            'ID region': 'id_region',
            'Region': 'region_nombre',
            'Mercado': 'mercado_nombre',
            'Subsector': 'subsector',
            'Producto': 'producto_nombre',
            'Variedad / Tipo': 'variedad_tipo',
            'Calidad': 'calidad',
            'Unidad de comercializacion': 'unidad_comercializacion',
            'Origen': 'origen',
            'Volumen': 'volumen',
            'Precio minimo': 'precio_minimo',
            'Precio maximo': 'precio_maximo',
            'Precio promedio': 'precio_promedio'
        }

        # Cache de datos existentes
        regiones_cache = {r.id_region: r for r in Region.objects.all()}
        mercados_cache = {}
        productos_cache = {}

        for i, df in enumerate(chunk_iter):
            if i < chunk_inicio:
                continue  # saltar chunks ya procesados

            self.stdout.write(f'🧩 Chunk {i} procesando...')
            df.columns = [c.strip().replace('\ufeff', '') for c in df.columns]
            df = df.rename(columns=mapeo_columnas)
            df = self.limpiar_datos(df)

            nuevos_registros = []
            for _, row in df.iterrows():
                try:
                    if pd.isna(row.get('id_region')) or pd.isna(row.get('producto_nombre')):
                        continue

                    # Obtener o crear Region en cache
                    id_region = int(row['id_region'])
                    region = regiones_cache.get(id_region)
                    if not region:
                        region = Region.objects.create(id_region=id_region, nombre=row['region_nombre'])
                        regiones_cache[id_region] = region

                    # Cache de mercado (clave: region + nombre)
                    key_mercado = (region.id_region, row['mercado_nombre'])
                    if key_mercado not in mercados_cache:
                        mercado, _ = Mercado.objects.get_or_create(nombre=row['mercado_nombre'], region=region)
                        mercados_cache[key_mercado] = mercado
                    else:
                        mercado = mercados_cache[key_mercado]

                    # Cache de producto (clave compuesta)
                    key_producto = (
                        row['producto_nombre'],
                        row['subsector'],
                        row['variedad_tipo'],
                        row['calidad'],
                        row['unidad_comercializacion'],
                        row['origen']
                    )
                    if key_producto not in productos_cache:
                        producto, _ = Producto.objects.get_or_create(
                            nombre=row['producto_nombre'],
                            subsector=row['subsector'],
                            variedad_tipo=row['variedad_tipo'],
                            calidad=row['calidad'],
                            unidad_comercializacion=row['unidad_comercializacion'],
                            origen=row['origen']
                        )
                        productos_cache[key_producto] = producto
                    else:
                        producto = productos_cache[key_producto]

                    # Fecha segura
                    try:
                        fecha = datetime.strptime(str(row['fecha']), '%Y-%m-%d').date()
                    except Exception:
                        continue

                    # Crear instancia (sin guardar todavía)
                    nuevos_registros.append(
                        PrecioDatos(
                            fecha=fecha,
                            region=region,
                            mercado=mercado,
                            producto=producto,
                            volumen=decimal.Decimal(str(row['volumen'])),
                            precio_minimo=decimal.Decimal(str(row['precio_minimo'])),
                            precio_maximo=decimal.Decimal(str(row['precio_maximo'])),
                            precio_promedio=decimal.Decimal(str(row['precio_promedio']))
                        )
                    )

                except Exception as e:
                    continue  # errores se omiten en grandes volúmenes

            # Guardar por bloques en DB
            try:
                with transaction.atomic():
                    PrecioDatos.objects.bulk_create(
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
        numeric_columns = ['volumen', 'precio_minimo', 'precio_maximo', 'precio_promedio']
        for col in numeric_columns:
            if col in df.columns:
                df[col] = df[col].astype(str)
                df[col] = df[col].str.replace('.', '', regex=False)
                df[col] = df[col].str.replace(',', '.', regex=False)
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

        text_columns = ['region_nombre', 'mercado_nombre', 'subsector', 'producto_nombre',
                        'variedad_tipo', 'calidad', 'unidad_comercializacion', 'origen']
        for col in text_columns:
            if col in df.columns:
                df[col] = df[col].astype(str).str.strip()
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
