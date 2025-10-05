import os
import pandas as pd
from django.core.management.base import BaseCommand
from datos.models import Region, Mercado, Producto, PrecioDatos
from datetime import datetime
import decimal

class Command(BaseCommand):
    help = 'Carga datos desde archivos CSV a la base de datos'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--ruta',
            type=str,
            help='Ruta de la carpeta con archivos CSV',
            default='data/'
        )
    
    def handle(self, *args, **options):
        ruta_carpeta = options['ruta']
        
        # Buscar archivos CSV en la carpeta
        archivos_csv = []
        for archivo in os.listdir(ruta_carpeta):
            if archivo.endswith('.csv'):
                archivos_csv.append(archivo)
        
        if not archivos_csv:
            self.stdout.write(self.style.WARNING('No se encontraron archivos CSV en la carpeta'))
            return
        
        self.stdout.write(f'Archivos CSV encontrados: {archivos_csv}')
        
        for archivo in archivos_csv:
            ruta_completa = os.path.join(ruta_carpeta, archivo)
            
            if os.path.exists(ruta_completa):
                self.stdout.write(f'Procesando {ruta_completa}')
                self.cargar_datos_desde_csv(ruta_completa)
            else:
                self.stdout.write(self.style.WARNING(f'Archivo no encontrado: {ruta_completa}'))
    
    def cargar_datos_desde_csv(self, ruta_archivo):
        try:
            # Leer CSV con encoding UTF-8-SIG (que detectó correctamente)
            df = pd.read_csv(ruta_archivo, encoding='UTF-8-SIG', delimiter=',')
            
            self.stdout.write(f"Columnas originales: {list(df.columns)}")
            self.stdout.write(f"Número de filas: {len(df)}")
            
            # Mostrar primeras filas para debug
            self.stdout.write("Primeras 2 filas del DataFrame:")
            for i in range(min(2, len(df))):
                self.stdout.write(f"Fila {i}: {df.iloc[i].to_dict()}")
            
            # Limpiar nombres de columnas (eliminar BOM si existe)
            df.columns = [col.strip().replace('\ufeff', '') for col in df.columns]
            self.stdout.write(f"Columnas después de limpieza: {list(df.columns)}")
            
            # Mapeo directo de columnas basado en lo que vemos
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
            
            # Renombrar columnas
            df = df.rename(columns=mapeo_columnas)
            self.stdout.write(f"Columnas después de renombrar: {list(df.columns)}")
            
            # Limpiar y convertir datos
            df = self.limpiar_datos(df)
            
            registros_procesados = 0
            registros_creados = 0
            
            for index, row in df.iterrows():
                try:
                    # Saltar filas vacías
                    if pd.isna(row.get('id_region')) or pd.isna(row.get('producto_nombre')):
                        continue
                    
                    # Obtener o crear Región
                    region, created_region = Region.objects.get_or_create(
                        id_region=int(row['id_region']),
                        defaults={'nombre': row['region_nombre']}
                    )
                    
                    # Obtener o crear Mercado
                    mercado, created_mercado = Mercado.objects.get_or_create(
                        nombre=row['mercado_nombre'],
                        region=region
                    )
                    
                    # Obtener o crear Producto
                    producto, created_producto = Producto.objects.get_or_create(
                        subsector=row['subsector'],
                        nombre=row['producto_nombre'],
                        variedad_tipo=row['variedad_tipo'],
                        calidad=row['calidad'],
                        unidad_comercializacion=row['unidad_comercializacion'],
                        origen=row['origen']
                    )
                    
                    # Convertir fecha
                    try:
                        fecha = datetime.strptime(str(row['fecha']), '%Y-%m-%d').date()
                    except ValueError as e:
                        self.stdout.write(self.style.WARNING(f'Fecha inválida: {row["fecha"]} - Error: {e}'))
                        continue
                    
                    # Crear registro de precios
                    precio_datos, created = PrecioDatos.objects.get_or_create(
                        fecha=fecha,
                        region=region,
                        mercado=mercado,
                        producto=producto,
                        defaults={
                            'volumen': decimal.Decimal(str(row['volumen'])),
                            'precio_minimo': decimal.Decimal(str(row['precio_minimo'])),
                            'precio_maximo': decimal.Decimal(str(row['precio_maximo'])),
                            'precio_promedio': decimal.Decimal(str(row['precio_promedio']))
                        }
                    )
                    
                    if created:
                        registros_creados += 1
                    
                    registros_procesados += 1
                    
                    if registros_procesados % 100 == 0:
                        self.stdout.write(f'Procesados {registros_procesados} registros...')
                    
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'Error procesando fila {index}: {e}'))
                    if index < 3:  # Mostrar detalles solo para las primeras filas con error
                        self.stdout.write(self.style.ERROR(f'Datos de la fila: {dict(row)}'))
                    continue
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'Archivo {ruta_archivo} procesado: {registros_procesados} registros procesados, {registros_creados} nuevos registros creados'
                )
            )
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error procesando archivo {ruta_archivo}: {e}'))
            import traceback
            self.stdout.write(self.style.ERROR(traceback.format_exc()))
    
    def limpiar_datos(self, df):
        """Limpia y convierte los datos del DataFrame"""
        
        # Reemplazar comas por puntos en números y convertir a float
        numeric_columns = ['volumen', 'precio_minimo', 'precio_maximo', 'precio_promedio']
        
        for col in numeric_columns:
            if col in df.columns:
                # Convertir a string
                df[col] = df[col].astype(str)
                
                # Para volumen (que ya está como entero en el ejemplo)
                if col == 'volumen':
                    df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
                else:
                    # Para precios que tienen formato "1652,0000"
                    # Eliminar comas de miles y reemplazar coma decimal por punto
                    df[col] = df[col].str.replace('.', '', regex=False)  # Eliminar separadores de miles
                    df[col] = df[col].str.replace(',', '.', regex=False)  # Reemplazar coma decimal por punto
                    df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        
        # Limpiar textos
        text_columns = ['region_nombre', 'mercado_nombre', 'subsector', 'producto_nombre', 
                       'variedad_tipo', 'calidad', 'unidad_comercializacion', 'origen']
        
        for col in text_columns:
            if col in df.columns:
                df[col] = df[col].astype(str).str.strip()
        
        return df