# AgroPreciosChile - Mapa Interactivo de Frutas y Hortalizas

## Descripción del Proyecto

AgroPreciosChile es una aplicación web interactiva que visualiza datos de comercialización de frutas y hortalizas en las diferentes regiones de Chile. La plataforma permite analizar precios, volúmenes y tendencias del mercado agrícola nacional.





## Características Implementadas

### [v1.0.0] - 2025-11-27
**Funcionalidades Principales**

- **Mapa Interactivo**: Visualización geográfica de las regiones de Chile con marcadores personalizados
- **Panel de Análisis Multi-Región**: Comparación simultánea de datos entre múltiples regiones
- **Sistema de Filtros Avanzados**: 
  - Filtrado por subsector (Frutas, Hortalizas, etc.)
  - Filtrado por producto específico
  - Filtrado por año de comercialización
- **Estadísticas**: 
  - Resumen general de la base de datos
  - Métricas por región seleccionada
  - Precios promedios, volúmenes y tendencias
    
- **Pedicciones con IA**
-  Predicciones por roducto y unidad en un horizonte de tiempo: 

**Características Técnicas**
- **Backend**: Django 4.2 con API RESTful
- **Frontend**: JavaScript vanilla con Leaflet para mapas
- **Base de Datos**: PostgreSQL con modelos optimizados
- **Interfaz**: CSS personalizado responsive
- **APIs**: Endpoints JSON para datos en tiempo real

### [v0.1.0-alpha] - 2025-8-15
**Fundamentos del Proyecto**
- Base del proyecto Django creada
- Configuración inicial y estructura de carpetas
- Templates HTML base implementados
- Modelos de base de datos diseñados y migrados
- Script para carga masiva de archivos CSV a la BD



##  Funcionalidades de Análisis

### Análisis Individual por Región
- Total de registros históricos
- Número de productos únicos
- Mercados activos en la región
- Subsectores principales
- Precios promedios por producto

### Análisis Comparativo Multi-Región
- Comparación de precios entre regiones
- Análisis de volúmenes comerciales
- Identificación de regiones con mejores precios
- Métricas de diferencia porcentual

##  Instalación y Configuración

1. **Requisitos**
   ```bash
   Python 3.8+
   PostgreSQL
   Django 4.2
   ```

2. **Instalación**
   ```bash
   pip install -r requirements.txt
   python manage.py migrate
   python manage.py loaddata datos_iniciales.json
   python manage.py runserver
   ```

3. **Carga de Datos**
   ```bash
   python manage.py cargar_csv archivo.csv
   ```


##  Interfaz de Usuario

- **Panel Lateral**: Estadísticas globales y filtros
- **Mapa Central**: Navegación por regiones
- **Panel de Región**: Detalles y productos por región
- **Análisis Multi-Región**: Comparación side-by-side

## Otras Características

Gráficos de tendencias temporales
Exportación de reportes en PDF/Excel


---

**Desarrollado para el análisis del mercado agrícola chileno** 🌱
