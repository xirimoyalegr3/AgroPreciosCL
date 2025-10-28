# AgroPreciosChile - Mapa Interactivo de Frutas y Hortalizas

## Descripción del Proyecto

AgroPreciosChile es una aplicación web interactiva que visualiza datos de comercialización de frutas y hortalizas en las diferentes regiones de Chile. La plataforma permite analizar precios, volúmenes y tendencias del mercado agrícola nacional.





## Características Implementadas

### [v1.0.0] - 2025-10-28
**Funcionalidades Principales**

- **Mapa Interactivo**: Visualización geográfica de las regiones de Chile con marcadores personalizados
- **Panel de Análisis Multi-Región**: Comparación simultánea de datos entre múltiples regiones
- **Sistema de Filtros Avanzados**: 
  - Filtrado por subsector (Frutas, Hortalizas, etc.)
  - Filtrado por producto específico
  - Filtrado por año de comercialización
- **Estadísticas en Tiempo Real**: 
  - Resumen general de la base de datos
  - Métricas por región seleccionada
  - Precios promedios, volúmenes y tendencias

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

## Estructura del Proyecto

```
AgroPreciosChile/
├── mapaInteractivo/          # App principal
│   ├── models.py            # Modelos de datos
│   ├── views.py             # Vistas y APIs
│   ├── urls.py              # Rutas de la aplicación
│   └── admin.py             # Panel de administración
├── templates/               # Plantillas HTML
├── static/                  # Archivos estáticos
│   ├── css/styles.css       # Estilos personalizados
│   └── js/mapa.js          # Lógica del mapa interactivo
└── AgroPreciosChile/        # Configuración del proyecto
    └── settings.py          # Configuraciones principales
```

##  Modelos de Datos

- **Region**: Divisiones territoriales de Chile
- **Mercado**: Locales de comercialización
- **Subsector**: Categorías (Frutas, Hortalizas, etc.)
- **Producto**: Productos específicos
- **Variedad**: Variedades de productos
- **DatosComercializacion**: Datos históricos de precios y volúmenes

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

##  APIs Disponibles

- `GET /api/resumen/` - Estadísticas generales
- `GET /api/region/<id>/` - Datos específicos de región
- `GET /api/region/<id>/productos/` - Productos por región
- `GET /api/filtros/` - Opciones de filtros disponibles
- `GET /api/comparar-regiones/` - Comparación multi-región

##  Interfaz de Usuario

- **Panel Lateral**: Estadísticas globales y filtros
- **Mapa Central**: Navegación por regiones
- **Panel de Región**: Detalles y productos por región
- **Análisis Multi-Región**: Comparación side-by-side

## Próximas Características

- [ ] Gráficos de tendencias temporales
- [ ] Exportación de reportes en PDF/Excel
- [En progreso] Predicción de precios.


---

**Desarrollado para el análisis del mercado agrícola chileno** 🌱
