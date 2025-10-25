// static/mapaInteractivo/js/mapa.js
class MapaInteractivo {
    constructor() {
        this.mapa = null;
        this.regionSeleccionada = null;
        this.filtros = {
            subsector: '',
            producto: '',
            año: ''
        };
        this.marcadoresRegiones = {};
        this.init();
    }

    init() {
        this.inicializarMapa();
        this.cargarResumenGeneral();
        this.cargarFiltrosDisponibles();
        this.agregarMarcadoresRegiones();
        this.configurarEventListeners();
    }

    inicializarMapa() {
        // Centro de Chile
        this.mapa = L.map('mapa').setView([-35.6751, -71.5430], 5);

        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '© OpenStreetMap contributors',
            maxZoom: 18,
            minZoom: 4
        }).addTo(this.mapa);

        // Añadir control de escala
        L.control.scale({imperial: false}).addTo(this.mapa);
    }

    async cargarResumenGeneral() {
        try {
            this.mostrarCargando('estadisticas-globales', 'Cargando estadísticas...');
            
            const response = await fetch('/api/resumen/');
            if (!response.ok) throw new Error(`Error HTTP: ${response.status}`);
            
            const data = await response.json();
            
            if (data.error) {
                throw new Error(data.error);
            }
            
            this.mostrarResumenGeneral(data);
        } catch (error) {
            console.error('Error cargando resumen:', error);
            this.mostrarError('estadisticas-globales', 'No se pudieron cargar las estadísticas generales');
        }
    }

    mostrarResumenGeneral(data) {
        const contenedor = document.getElementById('estadisticas-globales');
        
        let fechaReciente = 'N/A';
        if (data.fecha_reciente) {
            const fecha = new Date(data.fecha_reciente);
            fechaReciente = fecha.toLocaleDateString('es-CL');
        }

        contenedor.innerHTML = `
            <div class="estadistica-item">
                <span>📊 Total registros:</span>
                <span class="estadistica-valor">${data.total_registros?.toLocaleString('es-CL') || '0'}</span>
            </div>
            <div class="estadistica-item">
                <span>🗺️ Regiones:</span>
                <span class="estadistica-valor">${data.total_regiones || '0'}</span>
            </div>
            <div class="estadistica-item">
                <span>🍎 Productos:</span>
                <span class="estadistica-valor">${data.total_productos || '0'}</span>
            </div>
            <div class="estadistica-item">
                <span>🏪 Mercados:</span>
                <span class="estadistica-valor">${data.total_mercados || '0'}</span>
            </div>
            <div class="estadistica-item">
                <span>📅 Última fecha:</span>
                <span class="estadistica-valor">${fechaReciente}</span>
            </div>
        `;
    }

    async cargarFiltrosDisponibles() {
        try {
            this.mostrarCargando('filtros-container', 'Cargando filtros...');
            
            const response = await fetch('/api/filtros/');
            if (!response.ok) throw new Error(`Error HTTP: ${response.status}`);
            
            const data = await response.json();
            
            if (data.error) {
                throw new Error(data.error);
            }
            
            this.mostrarFiltros(data);
        } catch (error) {
            console.error('Error cargando filtros:', error);
            this.mostrarError('filtros-container', 'No se pudieron cargar los filtros');
        }
    }

// En mapa.js - REEMPLAZAR las funciones relacionadas con filtros
mostrarFiltros(data) {
    const contenedor = document.getElementById('filtros-container');
    
    // Crear opciones para años
    let opcionesAños = '<option value="">Todos los años</option>';
    if (data.años && data.años.length > 0) {
        data.años.forEach(año => {
            opcionesAños += `<option value="${año}">${año}</option>`;
        });
    }

    // Crear opciones para subsectores
    let opcionesSubsectores = '<option value="">Todos los subsectores</option>';
    if (data.subsectores && data.subsectores.length > 0) {
        data.subsectores.forEach(subsector => {
            opcionesSubsectores += `<option value="${subsector.nombre}">${subsector.nombre}</option>`;
        });
    }

    // Crear opciones para productos - CORRECCIÓN: usar select en lugar de input
    let opcionesProductos = '<option value="">Todos los productos</option>';
    if (data.productos && data.productos.length > 0) {
        // Ordenar productos alfabéticamente
        const productosOrdenados = data.productos.sort((a, b) => a.nombre.localeCompare(b.nombre));
        productosOrdenados.forEach(producto => {
            opcionesProductos += `<option value="${producto.nombre}">${producto.nombre}</option>`;
        });
    }

    contenedor.innerHTML = `
        <h3>🔍 Filtros</h3>
        <div class="filtro-grupo">
            <label for="filtro-subsector">Subsector:</label>
            <select id="filtro-subsector" class="filtro-select">
                ${opcionesSubsectores}
            </select>
        </div>
        <div class="filtro-grupo">
            <label for="filtro-producto">Producto:</label>
            <select id="filtro-producto" class="filtro-select">
                ${opcionesProductos}
            </select>
        </div>
        <div class="filtro-grupo">
            <label for="filtro-año">Año:</label>
            <select id="filtro-año" class="filtro-select">
                ${opcionesAños}
            </select>
        </div>
        <div class="botones-filtros">
            <button id="aplicar-filtros" class="btn-filtro btn-primario">Aplicar Filtros</button>
            <button id="limpiar-filtros" class="btn-filtro btn-secundario">Limpiar</button>
        </div>
    `;

    // Configurar event listeners simples
    document.getElementById('aplicar-filtros').addEventListener('click', () => this.aplicarFiltros());
    document.getElementById('limpiar-filtros').addEventListener('click', () => this.limpiarFiltros());
}

aplicarFiltros() {
    this.filtros = {
        subsector: document.getElementById('filtro-subsector').value,
        producto: document.getElementById('filtro-producto').value,
        año: document.getElementById('filtro-año').value
    };

    // Si hay una región seleccionada, recargar sus datos con los filtros
    if (this.regionSeleccionada) {
        this.cargarProductosRegion(this.regionSeleccionada);
    }
}

limpiarFiltros() {
    document.getElementById('filtro-subsector').value = '';
    document.getElementById('filtro-producto').value = '';
    document.getElementById('filtro-año').value = '';
    this.filtros = { subsector: '', producto: '', año: '' };
    
    if (this.regionSeleccionada) {
        this.cargarProductosRegion(this.regionSeleccionada);
    }
}


    mostrarFiltrosActivos() {
        let filtrosActivos = document.getElementById('filtros-activos');
        if (!filtrosActivos) {
            filtrosActivos = document.createElement('div');
            filtrosActivos.id = 'filtros-activos';
            filtrosActivos.className = 'filtros-activos';
            document.getElementById('filtros-container').appendChild(filtrosActivos);
        }

        const filtrosTexto = [];
        if (this.filtros.subsector) filtrosTexto.push(`Subsector: ${this.filtros.subsector}`);
        if (this.filtros.producto) filtrosTexto.push(`Producto: ${this.filtros.producto}`);
        if (this.filtros.año) filtrosTexto.push(`Año: ${this.filtros.año}`);

        filtrosActivos.innerHTML = `
            <strong>Filtros activos:</strong>
            <div>${filtrosTexto.join(' • ')}</div>
        `;
    }

    ocultarFiltrosActivos() {
        const filtrosActivos = document.getElementById('filtros-activos');
        if (filtrosActivos) {
            filtrosActivos.remove();
        }
    }

// En mapa.js - REEMPLAZAR completamente la función
agregarMarcadoresRegiones() {
    // SOLO las 9 regiones que EXISTEN según tus datos
    const regionesConDatos = [
        { id: 4, nombre: 'Región de Coquimbo', lat: -30.600, lng: -71.200, color: '#4ECDC4' },
        { id: 5, nombre: 'Región de Valparaíso', lat: -33.046, lng: -71.620, color: '#45B7D1' },
        { id: 7, nombre: 'Región del Maule', lat: -35.426, lng: -71.668, color: '#96CEB4' },
        { id: 8, nombre: 'Región del Biobío', lat: -36.827, lng: -73.050, color: '#FFEAA7' },
        { id: 9, nombre: 'Región de La Araucanía', lat: -38.736, lng: -72.591, color: '#DDA0DD' },
        { id: 10, nombre: 'Región de Los Lagos', lat: -41.469, lng: -72.942, color: '#98D8C8' },
        { id: 13, nombre: 'Región Metropolitana de Santiago', lat: -33.449, lng: -70.669, color: '#F7DC6F' },
        { id: 15, nombre: 'Región de Arica y Parinacota', lat: -18.478, lng: -70.312, color: '#BB8FCE' },
        { id: 16, nombre: 'Región de Ñuble', lat: -36.624, lng: -71.957, color: '#85C1E9' }
    ];

    // Limpiar marcadores existentes
    Object.values(this.marcadoresRegiones).forEach(marker => {
        this.mapa.removeLayer(marker);
    });
    this.marcadoresRegiones = {};

    regionesConDatos.forEach(region => {
        const iconoPersonalizado = L.divIcon({
            className: 'marker-region',
            html: `<div style="background-color: ${region.color}; width: 20px; height: 20px; border-radius: 50%; border: 3px solid white; box-shadow: 0 2px 5px rgba(0,0,0,0.3);"></div>`,
            iconSize: [26, 26],
            iconAnchor: [13, 13]
        });

        const marcador = L.marker([region.lat, region.lng], { 
            icon: iconoPersonalizado
        }).addTo(this.mapa);

        this.marcadoresRegiones[region.id] = marcador;

        marcador.bindTooltip(region.nombre, {
            permanent: false,
            direction: 'top',
            offset: [0, -10]
        });

        marcador.bindPopup(`
            <div class="popup-region">
                <h4>${region.nombre}</h4>
                <button class="btn-ver-detalles" onclick="app.seleccionarRegion(${region.id})">
                    📈 Ver Estadísticas
                </button>
            </div>
        `);

        marcador.on('click', () => {
            this.seleccionarRegion(region.id);
        });
    });
}

async seleccionarRegion(regionId) {
    try {
        // Verificar si la región existe en nuestros marcadores
        if (!this.marcadoresRegiones[regionId]) {
            console.warn(`Región ${regionId} no está en el mapa`);
            return;
        }

        this.regionSeleccionada = regionId;
        this.mostrarCargando('info-region', 'Cargando información de la región...');
        
        // Resaltar marcador seleccionado
        this.resaltarRegionSeleccionada(regionId);
        
        // Cargar datos básicos de la región
        const responseRegion = await fetch(`/api/region/${regionId}/`);
        if (!responseRegion.ok) {
            throw new Error(`Error cargando región: ${responseRegion.status}`);
        }
        
        const dataRegion = await responseRegion.json();
        
        if (dataRegion.error) {
            throw new Error(dataRegion.error);
        }
        
        this.mostrarInfoRegion(dataRegion);
        
        // Cargar productos de la región
        this.cargarProductosRegion(regionId);
        
    } catch (error) {
        console.error('Error seleccionando región:', error);
        this.mostrarError('info-region', 'Error cargando la región seleccionada');
    }
}
    resaltarRegionSeleccionada(regionId) {
        // Quitar resaltado de todos los marcadores
        Object.values(this.marcadoresRegiones).forEach(marcador => {
            const icon = marcador.getIcon();
            if (icon.options && icon.options.className) {
                marcador.setIcon(L.divIcon({
                    ...icon.options,
                    className: icon.options.className.replace(' selected', '')
                }));
            }
        });

        // Resaltar marcador seleccionado
        const marcadorSeleccionado = this.marcadoresRegiones[regionId];
        if (marcadorSeleccionado) {
            const icon = marcadorSeleccionado.getIcon();
            marcadorSeleccionado.setIcon(L.divIcon({
                ...icon.options,
                className: icon.options.className + ' selected'
            }));
        }
    }

mostrarInfoRegion(data) {
    console.log('Datos de región recibidos:', data); // DEBUG
    
    const contenedor = document.getElementById('info-region');
    
    // CORRECCIÓN: Formatear subsectores correctamente
    let subsectoresHTML = '';
    if (data.subsectores && data.subsectores.length > 0) {
        subsectoresHTML = data.subsectores.slice(0, 5).map(subsector => {
            // CORRECCIÓN: Usar subsector.nombre en lugar de subsector.nombre
            const nombreSubsector = subsector.nombre || 'Sin nombre';
            return `<span class="badge">${nombreSubsector} (${subsector.total})</span>`;
        }).join('');
    }

    contenedor.innerHTML = `
        <div class="region-header">
            <h3>📍 ${data.region_nombre}</h3>
            <div class="region-stats">
                <div class="stat-item">
                    <span class="stat-number">${data.total_registros?.toLocaleString('es-CL') || '0'}</span>
                    <span class="stat-label">registros</span>
                </div>
                <div class="stat-item">
                    <span class="stat-number">${data.total_productos || '0'}</span>
                    <span class="stat-label">productos</span>
                </div>
                <div class="stat-item">
                    <span class="stat-number">${data.total_mercados || '0'}</span>
                    <span class="stat-label">mercados</span>
                </div>
            </div>
        </div>
        ${subsectoresHTML ? `
            <div class="subsectores-section">
                <h4>🌿 Subsectores principales:</h4>
                <div class="subsectores-list">
                    ${subsectoresHTML}
                </div>
            </div>
        ` : ''}
        <div class="productos-section">
            <h4>📦 Productos disponibles:</h4>
            <div id="lista-productos" class="productos-list">
                <p>Cargando productos...</p>
            </div>
        </div>
    `;
    
    // Cargar los productos específicos de esta región en el filtro
    this.cargarProductosFiltroRegion(data.region_id);
}

async cargarProductosRegion(regionId) {
    try {
        this.mostrarCargando('lista-productos', 'Cargando productos...');
        
        // Construir URL con filtros
        const params = new URLSearchParams();
        if (this.filtros.subsector) params.append('subsector', this.filtros.subsector);
        if (this.filtros.producto) params.append('producto', this.filtros.producto);
        if (this.filtros.año) params.append('año', this.filtros.año);
        
        const url = `/api/region/${regionId}/productos/?${params.toString()}`;
        const response = await fetch(url);
        
        if (!response.ok) {
            throw new Error(`Error HTTP: ${response.status}`);
        }
        
        const data = await response.json();
        
        if (data.error) {
            throw new Error(data.error);
        }
        
        this.mostrarProductosRegion(data);
        
    } catch (error) {
        console.error('Error cargando productos:', error);
        this.mostrarError('lista-productos', 'Error cargando productos');
    }
}

async cargarProductosFiltroRegion(regionId) {
    try {
        const response = await fetch(`/api/region/${regionId}/productos/`);
        if (!response.ok) throw new Error('Error cargando productos de la región');
        
        const data = await response.json();
        
        if (data.productos && data.productos.length > 0) {
            const selectProducto = document.getElementById('filtro-producto');
            let opciones = '<option value="">Todos los productos</option>';
            
            // Ordenar productos alfabéticamente y eliminar duplicados
            const productosUnicos = [];
            const nombresVistos = new Set();
            
            data.productos.forEach(producto => {
                const nombreProducto = producto.producto__nombre;
                if (nombreProducto && !nombresVistos.has(nombreProducto)) {
                    nombresVistos.add(nombreProducto);
                    productosUnicos.push({
                        nombre: nombreProducto
                    });
                }
            });
            
            // Ordenar alfabéticamente
            productosUnicos.sort((a, b) => a.nombre.localeCompare(b.nombre));
            
            // Crear opciones
            productosUnicos.forEach(producto => {
                opciones += `<option value="${producto.nombre}">${producto.nombre}</option>`;
            });
            
            selectProducto.innerHTML = opciones;
        }
        
    } catch (error) {
        console.error('Error cargando productos para filtro:', error);
    }
}


mostrarProductosRegion(data) {
    console.log('Datos recibidos para productos:', data); // DEBUG
    
    const contenedor = document.getElementById('lista-productos');
    
    if (!data.productos || data.productos.length === 0) {
        contenedor.innerHTML = `
            <div class="sin-resultados">
                <p>🚫 No se encontraron productos</p>
                <p class="texto-pequeno">Prueba ajustando los filtros</p>
            </div>
        `;
        return;
    }

    const productosHTML = data.productos.map(producto => {
        console.log('Procesando producto:', producto); // DEBUG
        
        // CORRECCIÓN: Manejar valores nulos y conversiones
        const precioPromedio = producto.precio_promedio ? 
            parseFloat(producto.precio_promedio) : 0;
        const volumenTotal = producto.volumen_total ? 
            parseFloat(producto.volumen_total) : 0;
        
        return `
            <div class="producto-item">
                <div class="producto-header">
                    <strong class="producto-nombre">${producto.producto__nombre || 'Nombre no disponible'}</strong>
                    <span class="producto-subsector">${producto.subsector__nombre || 'Sin subsector'}</span>
                </div>
                <div class="producto-stats">
                    <div class="producto-stat">
                        <span>Precio promedio:</span>
                        <strong>$${precioPromedio.toFixed(2)}</strong>
                    </div>
                    <div class="producto-stat">
                        <span>Volumen:</span>
                        <strong>${volumenTotal.toLocaleString('es-CL')}</strong>
                    </div>
                    <div class="producto-stat">
                        <span>Registros:</span>
                        <strong>${producto.total_registros || '0'}</strong>
                    </div>
                </div>
            </div>
        `;
    }).join('');

    contenedor.innerHTML = `
        <div class="resultados-info">
            <p class="texto-pequeno">Mostrando ${data.total_resultados} productos</p>
            ${data.filtros_aplicados && (data.filtros_aplicados.producto || data.filtros_aplicados.subsector || data.filtros_aplicados.año) ? 
                `<p class="texto-pequeno filtros-aplicados">Con filtros aplicados</p>` : ''
            }
        </div>
        ${productosHTML}
    `;
}

    mostrarCargando(elementId, mensaje = 'Cargando...') {
        const elemento = document.getElementById(elementId);
        if (elemento) {
            elemento.innerHTML = `<div class="cargando">⏳ ${mensaje}</div>`;
        }
    }

    mostrarError(elementId, mensaje = 'Error al cargar los datos') {
        const elemento = document.getElementById(elementId);
        if (elemento) {
            elemento.innerHTML = `<div class="error">❌ ${mensaje}</div>`;
        }
    }
}



// Inicializar la aplicación cuando se carga la página
document.addEventListener('DOMContentLoaded', function() {
    window.app = new MapaInteractivo();
});