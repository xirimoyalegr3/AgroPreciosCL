import os
import json
import pandas as pd
from django.core.management.base import BaseCommand
from mapaInteractivo.models import (Region, Mercado, Subsector, Producto, 
                                   Variedad, DatosComercializacion)
from datetime import datetime
import decimal
from django.db import transaction
import re

class Command(BaseCommand):
    help = 'Carga masiva optimizada y permisiva desde CSVs'

    def add_arguments(self, parser):
        parser.add_argument('--ruta', type=str, default='datos/', help='Carpeta con los CSV')
        parser.add_argument('--archivo', type=str, help='Procesar un archivo específico')
        parser.add_argument('--debug', action='store_true', help='Modo debug con más logging')
        parser.add_argument('--reset', action='store_true', help='Resetear progreso y empezar desde 0')

    def handle(self, *args, **options):
        ruta_carpeta = options['ruta']
        archivo_especifico = options.get('archivo')
        debug_mode = options.get('debug', False)
        reset_progress = options.get('reset', False)
        
        progreso_path = os.path.join(ruta_carpeta, 'progreso_carga.json')
        
        if reset_progress and os.path.exists(progreso_path):
            os.remove(progreso_path)
            self.stdout.write(self.style.WARNING('Progreso resetado'))
        
        progreso = self.cargar_progreso(progreso_path)

        # Obtener archivos CSV
        if archivo_especifico:
            archivos_csv = [archivo_especifico]
        else:
            archivos_csv = [a for a in os.listdir(ruta_carpeta) if a.endswith('.csv')]
        
        if not archivos_csv:
            self.stdout.write(self.style.WARNING('No hay archivos CSV'))
            return

        for archivo in archivos_csv:
            ruta_completa = os.path.join(ruta_carpeta, archivo)
            if not os.path.exists(ruta_completa):
                self.stdout.write(self.style.WARNING(f'Archivo no encontrado: {ruta_completa}'))
                continue

            chunk_actual = progreso.get(archivo, 0)
            self.stdout.write(f'📁 Procesando {archivo} desde chunk {chunk_actual}...')
            
            if debug_mode:
                self.verificar_archivo(ruta_completa, archivo)
            
            self.cargar_en_chunks(ruta_completa, archivo, progreso_path, progreso, chunk_actual, debug_mode)

        self.stdout.write(self.style.SUCCESS('✅ Carga completa.'))

    def verificar_archivo(self, ruta_archivo, nombre_archivo):
        """Verificar contenido del archivo para debugging"""
        try:
            df = pd.read_csv(ruta_archivo, encoding='utf-8', nrows=1000)
            self.stdout.write(f"=== DEBUG {nombre_archivo} ===")
            self.stdout.write(f"📊 Total filas: {len(pd.read_csv(ruta_archivo, encoding='utf-8'))}")
            self.stdout.write(f"📋 Columnas: {list(df.columns)}")
            
            # Verificar regiones
            if 'ID region' in df.columns:
                regiones_unicas = df['ID region'].value_counts()
                self.stdout.write(f"�️ Regiones encontradas:")
                for region_id, count in regiones_unicas.items():
                    self.stdout.write(f"   - ID {region_id}: {count} registros")
            
            # Muestra de datos problemáticos
            self.stdout.write("🔍 Muestra de datos:")
            for i in range(min(3, len(df))):
                row = df.iloc[i]
                self.stdout.write(f"   Fila {i}: Región {row.get('ID region', 'N/A')} | {row.get('Producto', 'N/A')} | Vol: {row.get('Volumen', 'N/A')}")
            
            self.stdout.write("=== FIN DEBUG ===")
            
        except Exception as e:
            self.stdout.write(f"❌ ERROR leyendo archivo {nombre_archivo}: {e}")

    def cargar_en_chunks(self, ruta_archivo, nombre_archivo, progreso_path, progreso, chunk_inicio=0, debug_mode=False):
        chunk_size = 50000
        total_registros_procesados = 0
        registros_exitosos = 0
        errores_totales = 0
        
        try:
            chunk_iter = pd.read_csv(ruta_archivo, encoding='utf-8', delimiter=',', chunksize=chunk_size)
            
            # Cache de datos existentes
            regiones_cache = {r.id_region: r for r in Region.objects.all()}
            mercados_cache = {m.nombre: m for m in Mercado.objects.all()}
            subsectores_cache = {s.nombre: s for s in Subsector.objects.all()}
            productos_cache = {}
            variedades_cache = {}

            for i, df in enumerate(chunk_iter):
                if i < chunk_inicio:
                    continue

                self.stdout.write(f'🔄 Chunk {i} procesando ({len(df)} filas)...')
                
                # Limpiar nombres de columnas
                df.columns = [self.limpiar_nombre_columna(c) for c in df.columns]
                
                df = self.limpiar_y_validar_datos(df, debug_mode)
                total_registros_procesados += len(df)

                nuevos_registros = []
                errores_chunk = 0
                
                for j, row in df.iterrows():
                    try:
                        # DEBUG: Mostrar cada 1000 filas
                        if debug_mode and j % 1000 == 0:
                            self.stdout.write(f"   Procesando fila {j}...")

                        # 🔹 VALIDACIÓN PERMISIVA DE DATOS ESENCIALES
                        datos_validos = self.validar_fila_permisiva(row)
                        if not datos_validos['valida']:
                            if debug_mode and errores_chunk < 5:
                                self.stdout.write(f"   ⚠️ Fila {j} saltada: {datos_validos['razon']}")
                            errores_chunk += 1
                            continue

                        # 🔹 OBTENER O CREAR REGIÓN (MÁS ROBUSTO)
                        region = self.obtener_o_crear_region(
                            datos_validos['id_region'], 
                            datos_validos['nombre_region'],
                            regiones_cache,
                            debug_mode
                        )
                        if not region:
                            errores_chunk += 1
                            continue

                        # 🔹 OBTENER O CREAR MERCADO
                        mercado = self.obtener_o_crear_mercado(
                            datos_validos['mercado'],
                            mercados_cache,
                            debug_mode
                        )

                        # 🔹 OBTENER O CREAR SUBSECTOR
                        subsector = self.obtener_o_crear_subsector(
                            datos_validos['subsector'],
                            subsectores_cache,
                            debug_mode
                        )

                        # 🔹 OBTENER O CREAR PRODUCTO
                        producto = self.obtener_o_crear_producto(
                            datos_validos['producto'],
                            subsector,
                            productos_cache,
                            debug_mode
                        )

                        # 🔹 OBTENER O CREAR VARIEDAD (OPCIONAL)
                        variedad = self.obtener_o_crear_variedad(
                            datos_validos['variedad'],
                            producto,
                            variedades_cache,
                            debug_mode
                        )

                        # 🔹 CONVERTIR FECHA
                        fecha = self.convertir_fecha_permisiva(datos_validos['fecha'], debug_mode)
                        if not fecha:
                            errores_chunk += 1
                            continue

                        # 🔹 CONVERTIR VALORES NUMÉRICOS
                        valores_numericos = self.convertir_valores_numericos(row, debug_mode)
                        if not valores_numericos['valido']:
                            if debug_mode and errores_chunk < 3:
                                self.stdout.write(f"   ⚠️ Fila {j}: Error numérico")
                            errores_chunk += 1
                            continue

                        # 🔹 CREAR REGISTRO
                        nuevo_registro = DatosComercializacion(
                            fecha=fecha,
                            region=region,
                            mercado=mercado,
                            subsector=subsector,
                            producto=producto,
                            variedad=variedad,
                            calidad=datos_validos['calidad'],
                            unidad_comercializacion=datos_validos['unidad_comercializacion'],
                            origen=datos_validos['origen'],
                            volumen=valores_numericos['volumen'],
                            precio_minimo=valores_numericos['precio_minimo'],
                            precio_maximo=valores_numericos['precio_maximo'],
                            precio_promedio=valores_numericos['precio_promedio']
                        )
                        
                        nuevos_registros.append(nuevo_registro)
                        registros_exitosos += 1

                    except Exception as e:
                        errores_chunk += 1
                        errores_totales += 1
                        if debug_mode and errores_chunk <= 3:
                            self.stdout.write(f"   ❌ Fila {j}: Error inesperado - {e}")
                        continue

                # 🔹 GUARDAR BLOQUE EN BD
                try:
                    with transaction.atomic():
                        if nuevos_registros:
                            DatosComercializacion.objects.bulk_create(
                                nuevos_registros, 
                                batch_size=5000, 
                                ignore_conflicts=True
                            )
                            self.stdout.write(self.style.SUCCESS(
                                f'   ✅ Chunk {i}: {len(nuevos_registros)} registros guardados'
                            ))
                        else:
                            self.stdout.write(f'   ℹ️ Chunk {i}: Sin registros válidos')
                            
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'   ❌ Error guardando chunk {i}: {e}'))

                # 🔹 GUARDAR PROGRESO
                progreso[nombre_archivo] = i + 1
                self.guardar_progreso(progreso_path, progreso)

            # 🔹 RESUMEN DEL ARCHIVO
            self.stdout.write(self.style.SUCCESS(
                f'📊 Archivo {nombre_archivo} completado: '
                f'{registros_exitosos}/{total_registros_procesados} registros exitosos '
                f'({errores_totales} errores)'
            ))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Error procesando archivo {nombre_archivo}: {e}'))

    # ============================================================================
    # FUNCIONES AUXILIARES PERMISIVAS
    # ============================================================================

    def limpiar_nombre_columna(self, nombre):
        """Limpiar nombre de columna de manera robusta"""
        if not nombre:
            return 'columna_desconocida'
        return str(nombre).strip().replace('\ufeff', '').replace('"', '')

    def validar_fila_permisiva(self, row):
        """Validación MUY permisiva de fila"""
        try:
            # ID Región - intentar convertir de múltiples maneras
            id_region_raw = row.get('ID region', row.get('ID_region', row.get('RegionID', 0)))
            id_region = self.convertir_a_entero_permisivo(id_region_raw)
            
            if id_region == 0:
                return {'valida': False, 'razon': 'ID región inválido'}
            
            # Datos esenciales con valores por defecto
            nombre_region = str(row.get('Region', row.get('Región', f'Región {id_region}'))).strip()
            producto = str(row.get('Producto', 'Producto No Especificado')).strip()
            subsector = str(row.get('Subsector', 'Subsector No Especificado')).strip()
            
            if not producto or producto.lower() in ['nan', 'null', '']:
                producto = 'Producto No Especificado'
            if not subsector or subsector.lower() in ['nan', 'null', '']:
                subsector = 'Subsector No Especificado'

            return {
                'valida': True,
                'id_region': id_region,
                'nombre_region': nombre_region,
                'producto': producto,
                'subsector': subsector,
                'mercado': str(row.get('Mercado', 'Mercado No Especificado')).strip(),
                'variedad': str(row.get('Variedad / Tipo', row.get('Variedad', ''))).strip(),
                'calidad': str(row.get('Calidad', 'No Especificada')).strip(),
                'unidad_comercializacion': str(row.get('Unidad de comercializacion', 'No Especificada')).strip(),
                'origen': str(row.get('Origen', 'No Especificado')).strip(),
                'fecha': row.get('Fecha', '')
            }
            
        except Exception as e:
            return {'valida': False, 'razon': f'Error validación: {e}'}

    def convertir_a_entero_permisivo(self, valor):
        """Convertir a entero de manera muy permisiva"""
        try:
            if pd.isna(valor):
                return 0
            str_valor = str(valor).strip()
            if not str_valor or str_valor.lower() in ['nan', 'null', 'none', '']:
                return 0
            # Extraer números del string
            numeros = re.findall(r'\d+', str_valor)
            if numeros:
                return int(numeros[0])
            return 0
        except:
            return 0

    def obtener_o_crear_region(self, id_region, nombre_region, cache, debug=False):
        """Obtener o crear región de manera robusta"""
        try:
            if id_region in cache:
                return cache[id_region]
            
            region, created = Region.objects.get_or_create(
                id_region=id_region,
                defaults={'nombre': nombre_region}
            )
            cache[id_region] = region
            
            if debug and created:
                self.stdout.write(f"      🆕 Región creada: {nombre_region} (ID: {id_region})")
                
            return region
            
        except Exception as e:
            if debug:
                self.stdout.write(f"      ❌ Error creando región {id_region}: {e}")
            return None

    def obtener_o_crear_mercado(self, nombre_mercado, cache, debug=False):
        """Obtener o crear mercado"""
        try:
            nombre_limpio = nombre_mercado.strip()
            if not nombre_limpio:
                nombre_limpio = 'Mercado No Especificado'
                
            if nombre_limpio in cache:
                return cache[nombre_limpio]
            
            mercado, created = Mercado.objects.get_or_create(nombre=nombre_limpio)
            cache[nombre_limpio] = mercado
            return mercado
            
        except Exception:
            # Fallback: usar mercado por defecto
            return cache.get('Mercado No Especificado', Mercado.objects.get_or_create(nombre='Mercado No Especificado')[0])

    def obtener_o_crear_subsector(self, nombre_subsector, cache, debug=False):
        """Obtener o crear subsector"""
        try:
            nombre_limpio = nombre_subsector.strip()
            if not nombre_limpio:
                nombre_limpio = 'Subsector No Especificado'
                
            if nombre_limpio in cache:
                return cache[nombre_limpio]
            
            subsector, created = Subsector.objects.get_or_create(nombre=nombre_limpio)
            cache[nombre_limpio] = subsector
            return subsector
            
        except Exception:
            return cache.get('Subsector No Especificado', Subsector.objects.get_or_create(nombre='Subsector No Especificado')[0])

    def obtener_o_crear_producto(self, nombre_producto, subsector, cache, debug=False):
        """Obtener o crear producto"""
        try:
            nombre_limpio = nombre_producto.strip()
            if not nombre_limpio:
                nombre_limpio = 'Producto No Especificado'
                
            cache_key = (nombre_limpio, subsector.id)
            if cache_key in cache:
                return cache[cache_key]
            
            producto, created = Producto.objects.get_or_create(
                nombre=nombre_limpio,
                subsector=subsector
            )
            cache[cache_key] = producto
            return producto
            
        except Exception:
            # Producto genérico como fallback
            cache_key = ('Producto No Especificado', subsector.id)
            if cache_key in cache:
                return cache[cache_key]
            producto, _ = Producto.objects.get_or_create(
                nombre='Producto No Especificado',
                subsector=subsector
            )
            cache[cache_key] = producto
            return producto

    def obtener_o_crear_variedad(self, nombre_variedad, producto, cache, debug=False):
        """Obtener o crear variedad (opcional)"""
        try:
            nombre_limpio = nombre_variedad.strip()
            if not nombre_limpio or nombre_limpio.lower() in ['nan', 'null', 'sin especificar', '']:
                return None
                
            cache_key = (nombre_limpio, producto.id)
            if cache_key in cache:
                return cache[cache_key]
            
            variedad, created = Variedad.objects.get_or_create(
                nombre=nombre_limpio,
                producto=producto
            )
            cache[cache_key] = variedad
            return variedad
            
        except Exception:
            return None

    def convertir_fecha_permisiva(self, fecha_raw, debug=False):
        """Convertir fecha de múltiples formatos"""
        try:
            if pd.isna(fecha_raw):
                return None
                
            str_fecha = str(fecha_raw).strip()
            if not str_fecha:
                return None

            # Intentar múltiples formatos
            formatos = [
                '%Y-%m-%d',      # 2024-01-15
                '%d/%m/%Y',      # 15/01/2024
                '%d-%m-%Y',      # 15-01-2024
                '%Y/%m/%d',      # 2024/01/15
                '%m/%d/%Y',      # 01/15/2024 (formato US)
            ]
            
            for formato in formatos:
                try:
                    return datetime.strptime(str_fecha, formato).date()
                except ValueError:
                    continue
            
            # Si ningún formato funciona, usar pandas
            try:
                fecha_pd = pd.to_datetime(str_fecha, errors='coerce')
                if not pd.isna(fecha_pd):
                    return fecha_pd.date()
            except:
                pass
                
            if debug:
                self.stdout.write(f"      ⚠️ Fecha no reconocida: {str_fecha}")
            return None
            
        except Exception as e:
            if debug:
                self.stdout.write(f"      ❌ Error convirtiendo fecha {fecha_raw}: {e}")
            return None

    def convertir_valores_numericos(self, row, debug=False):
        """Convertir todos los valores numéricos de manera robusta"""
        try:
            volumen = self.convertir_decimal_super_permisivo(row.get('Volumen', 0))
            precio_minimo = self.convertir_decimal_super_permisivo(row.get('Precio minimo', 0))
            precio_maximo = self.convertir_decimal_super_permisivo(row.get('Precio maximo', 0))
            precio_promedio = self.convertir_decimal_super_permisivo(row.get('Precio promedio', 0))
            
            # Validar que los precios sean razonables
            if precio_minimo > 6000000 or precio_maximo > 6000000 or precio_promedio > 6000000:
                if debug:
                    self.stdout.write(f"      ⚠️ Precios muy altos: min={precio_minimo}, max={precio_maximo}")
                return {'valido': False}

            return {
                'valido': True,
                'volumen': volumen,
                'precio_minimo': precio_minimo,
                'precio_maximo': precio_maximo,
                'precio_promedio': precio_promedio
            }
            
        except Exception as e:
            if debug:
                self.stdout.write(f"      ❌ Error numérico: {e}")
            return {'valido': False}

    def convertir_decimal_super_permisivo(self, valor):
        """Conversión SUPER permisiva de decimales"""
        try:
            if pd.isna(valor):
                return decimal.Decimal('0')
            
            str_valor = str(valor).strip()
            
            # Casos especiales
            if not str_valor or str_valor.lower() in ['nan', 'null', 'none', '']:
                return decimal.Decimal('0')
            
            # Remover espacios
            str_valor = str_valor.replace(' ', '')
            
            # Manejar formato europeo (coma como decimal)
            if ',' in str_valor and '.' in str_valor:
                # Ej: "1.999,99" -> quitar puntos de miles, coma a punto
                str_valor = str_valor.replace('.', '').replace(',', '.')
            elif ',' in str_valor:
                # Ej: "1999,99" -> coma a punto
                str_valor = str_valor.replace(',', '.')
            # Si solo tiene puntos, verificar si es decimal o miles
            elif '.' in str_valor:
                parts = str_valor.split('.')
                if len(parts) == 2 and len(parts[1]) <= 2:
                    # Probablemente decimal (ej: "99.50")
                    pass  # Mantener como está
                else:
                    # Probablemente miles (ej: "1.999")
                    str_valor = str_valor.replace('.', '')
            
            # Convertir a decimal
            return decimal.Decimal(str_valor)
            
        except (ValueError, decimal.InvalidOperation):
            # Último intento: extraer solo números
            try:
                numeros = re.findall(r'\d+', str_valor)
                if numeros:
                    return decimal.Decimal(numeros[0])
                return decimal.Decimal('0')
            except:
                return decimal.Decimal('0')

    def limpiar_y_validar_datos(self, df, debug_mode=False):
        """Limpieza final permisiva del DataFrame"""
        # Asegurar que las columnas críticas existen
        columnas_requeridas = ['ID region', 'Producto', 'Subsector']
        for col in columnas_requeridas:
            if col not in df.columns:
                df[col] = 0 if col == 'ID region' else 'No Especificado'
        
        # Rellenar valores NaN
        df = df.fillna({
            'ID region': 0,
            'Region': 'Región No Especificada',
            'Mercado': 'Mercado No Especificado', 
            'Subsector': 'Subsector No Especificado',
            'Producto': 'Producto No Especificado',
            'Variedad / Tipo': '',
            'Calidad': 'No Especificada',
            'Unidad de comercializacion': 'No Especificada',
            'Origen': 'No Especificado',
            'Volumen': 0,
            'Precio minimo': 0,
            'Precio maximo': 0,
            'Precio promedio': 0
        })
        
        return df

    def cargar_progreso(self, ruta):
        if os.path.exists(ruta):
            with open(ruta, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}

    def guardar_progreso(self, ruta, data):
        with open(ruta, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)