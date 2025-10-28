// static/mapaInteractivo/js/mapa.js
class MapaInteractivo {
    constructor() {
        this.mapa = null;
        this.regionSeleccionada = null;
        this.regionesAnalisis = new Set();
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
        this.inicializarPanelAnalisis();
    }

    inicializarMapa() {
        this.mapa = L.map('mapa').setView([-35.6751, -71.5430], 5);

        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '© OpenStreetMap contributors',
            maxZoom: 18,
            minZoom: 4
        }).addTo(this.mapa);

        L.control.scale({imperial: false}).addTo(this.mapa);
    }

    configurarEventListeners() {
        document.addEventListener('change', (e) => {
            if (e.target.id === 'filtro-subsector') {
                this.actualizarProductosPorSubsector(e.target.value);
            }
        });
    }

    inicializarPanelAnalisis() {
        if (!document.getElementById('panel-analisis')) {
            const panelAnalisis = document.createElement('div');
            panelAnalisis.id = 'panel-analisis';
            panelAnalisis.className = 'panel-analisis';
            panelAnalisis.innerHTML = `
                <h3>Analisis Multi-Region</h3>
                <div id="lista-regiones-analisis" class="lista-regiones-analisis">
                    <p class="sin-region-seleccionada">No hay regiones seleccionadas para analisis</p>
                </div>
                <div class="botones-analisis">
                    <button id="comparar-regiones" class="btn-filtro btn-primario" disabled>Comparar Regiones</button>
                    <button id="limpiar-analisis" class="btn-filtro btn-secundario">Limpiar Analisis</button>
                </div>
            `;
            document.getElementById('panel-lateral').appendChild(panelAnalisis);

            document.getElementById('comparar-regiones').addEventListener('click', () => this.compararRegiones());
            document.getElementById('limpiar-analisis').addEventListener('click', () => this.limpiarAnalisis());
        }
    }

    // FUNCIONES DE UTILIDAD QUE FALTABAN
    mostrarCargando(elementId, mensaje = 'Cargando...') {
        const elemento = document.getElementById(elementId);
        if (elemento) {
            elemento.innerHTML = `<div class="cargando">${mensaje}</div>`;
        }
    }

    mostrarError(elementId, mensaje = 'Error al cargar los datos') {
        const elemento = document.getElementById(elementId);
        if (elemento) {
            elemento.innerHTML = `<div class="error">${mensaje}</div>`;
        }
    }

    mostrarMensaje(mensaje, tipo = 'info') {
        const mensajeElement = document.createElement('div');
        mensajeElement.className = `mensaje-temporal mensaje-${tipo}`;
        mensajeElement.textContent = mensaje;
        mensajeElement.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 12px 20px;
            border-radius: 6px;
            color: white;
            z-index: 10000;
            font-weight: 500;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        `;

        const colores = {
            success: '#28a745',
            error: '#dc3545',
            info: '#17a2b8',
            warning: '#ffc107'
        };

        mensajeElement.style.backgroundColor = colores[tipo] || colores.info;
        document.body.appendChild(mensajeElement);

        setTimeout(() => {
            if (mensajeElement.parentNode) {
                mensajeElement.parentNode.removeChild(mensajeElement);
            }
        }, 3000);
    }

    async cargarResumenGeneral() {
        try {
            this.mostrarCargando('estadisticas-globales', 'Cargando estadisticas...');
            
            const response = await fetch('/api/resumen/');
            if (!response.ok) throw new Error(`Error HTTP: ${response.status}`);
            
            const data = await response.json();
            
            if (data.error) {
                throw new Error(data.error);
            }
            
            this.mostrarResumenGeneral(data);
        } catch (error) {
            console.error('Error cargando resumen:', error);
            this.mostrarError('estadisticas-globales', 'No se pudieron cargar las estadisticas generales');
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
                <span>Total registros:</span>
                <span class="estadistica-valor">${data.total_registros?.toLocaleString('es-CL') || '0'}</span>
            </div>
            <div class="estadistica-item">
                <span>Regiones:</span>
                <span class="estadistica-valor">${data.total_regiones || '0'}</span>
            </div>
            <div class="estadistica-item">
                <span>Productos:</span>
                <span class="estadistica-valor">${data.total_productos || '0'}</span>
            </div>
            <div class="estadistica-item">
                <span>Mercados:</span>
                <span class="estadistica-valor">${data.total_mercados || '0'}</span>
            </div>
            <div class="estadistica-item">
                <span>Ultima fecha:</span>
                <span class="estadistica-valor">${fechaReciente}</span>
            </div>
        `;
    }

// REEMPLAZAR completamente las funciones relacionadas con filtros:

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

mostrarFiltros(data) {
    const contenedor = document.getElementById('filtros-container');
    
    // Corregir: eliminar años duplicados
    let opcionesAños = '<option value="">Todos los años</option>';
    if (data.años && data.años.length > 0) {
        const añosUnicos = [...new Set(data.años)]; // Eliminar duplicados
        añosUnicos.sort((a, b) => b - a); // Ordenar descendente
        añosUnicos.forEach(año => {
            opcionesAños += `<option value="${año}">${año}</option>`;
        });
    }

    let opcionesSubsectores = '<option value="">Todos los subsectores</option>';
    if (data.subsectores && data.subsectores.length > 0) {
        data.subsectores.forEach(subsector => {
            opcionesSubsectores += `<option value="${subsector.nombre}">${subsector.nombre}</option>`;
        });
    }

    let opcionesProductos = '<option value="">Todos los productos</option>';
    if (data.productos && data.productos.length > 0) {
        const productosOrdenados = data.productos.sort((a, b) => a.nombre.localeCompare(b.nombre));
        productosOrdenados.forEach(producto => {
            opcionesProductos += `<option value="${producto.nombre}">${producto.nombre}</option>`;
        });
    }

    contenedor.innerHTML = `
        <h3>Filtros</h3>
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

    // Configurar event listeners CORREGIDOS
    document.getElementById('filtro-subsector').addEventListener('change', (e) => {
        this.actualizarProductosPorSubsector(e.target.value);
    });

    document.getElementById('aplicar-filtros').addEventListener('click', () => this.aplicarFiltros());
    document.getElementById('limpiar-filtros').addEventListener('click', () => this.limpiarFiltros());
}

// REEMPLAZAR esta función completamente
async actualizarProductosPorSubsector(subsectorNombre) {
    try {
        const selectProducto = document.getElementById('filtro-producto');
        
        if (!subsectorNombre) {
            // Si no hay subsector, cargar todos los productos
            await this.cargarTodosLosProductos();
            return;
        }

        // Solo deshabilitar temporalmente, sin animaciones raras
        selectProducto.disabled = true;
        const valorOriginal = selectProducto.value;
        selectProducto.innerHTML = '<option value="">Cargando productos...</option>';

        // Buscar productos del subsector seleccionado
        const response = await fetch('/api/filtros/');
        const filtrosData = await response.json();
        
        let opciones = '<option value="">Todos los productos</option>';
        
        if (filtrosData.productos && filtrosData.productos.length > 0) {
            // Filtrar productos por subsector
            const productosFiltrados = filtrosData.productos.filter(producto => {
                // En una implementación real, aquí buscarías los productos del subsector
                // Por ahora, cargamos todos los productos y el filtro se aplica después
                return true;
            });
            
            const productosOrdenados = productosFiltrados.sort((a, b) => a.nombre.localeCompare(b.nombre));
            productosOrdenados.forEach(producto => {
                opciones += `<option value="${producto.nombre}">${producto.nombre}</option>`;
            });
        }
        
        selectProducto.innerHTML = opciones;
        selectProducto.disabled = false;
        selectProducto.value = valorOriginal; // Mantener el valor seleccionado si existe
        
    } catch (error) {
        console.error('Error actualizando productos:', error);
        const selectProducto = document.getElementById('filtro-producto');
        selectProducto.innerHTML = '<option value="">Error cargando productos</option>';
        selectProducto.disabled = false;
    }
}

// REEMPLAZAR esta función
async cargarTodosLosProductos() {
    try {
        const selectProducto = document.getElementById('filtro-producto');
        selectProducto.disabled = true;
        selectProducto.innerHTML = '<option value="">Cargando productos...</option>';

        const response = await fetch('/api/filtros/');
        const data = await response.json();
        
        let opciones = '<option value="">Todos los productos</option>';
        if (data.productos && data.productos.length > 0) {
            const productosOrdenados = data.productos.sort((a, b) => a.nombre.localeCompare(b.nombre));
            productosOrdenados.forEach(producto => {
                opciones += `<option value="${producto.nombre}">${producto.nombre}</option>`;
            });
        }
        
        selectProducto.innerHTML = opciones;
        selectProducto.disabled = false;
        
    } catch (error) {
        console.error('Error cargando todos los productos:', error);
        const selectProducto = document.getElementById('filtro-producto');
        selectProducto.innerHTML = '<option value="">Error cargando productos</option>';
        selectProducto.disabled = false;
    }
}

// MANTENER estas funciones igual
aplicarFiltros() {
    this.filtros = {
        subsector: document.getElementById('filtro-subsector').value,
        producto: document.getElementById('filtro-producto').value,
        año: document.getElementById('filtro-año').value
    };

    this.mostrarFiltrosActivos();

    if (this.regionSeleccionada) {
        this.cargarProductosRegion(this.regionSeleccionada);
    }
}

limpiarFiltros() {
    document.getElementById('filtro-subsector').value = '';
    document.getElementById('filtro-producto').value = '';
    document.getElementById('filtro-año').value = '';
    this.filtros = { subsector: '', producto: '', año: '' };
    this.ocultarFiltrosActivos();
    
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

    agregarMarcadoresRegiones() {
        const regionesConDatos = [
            { id: 4, nombre: 'Region de Coquimbo', lat: -30.600, lng: -71.200, color: '#4ECDC4' },
            { id: 5, nombre: 'Region de Valparaiso', lat: -33.046, lng: -71.620, color: '#45B7D1' },
            { id: 7, nombre: 'Region del Maule', lat: -35.426, lng: -71.668, color: '#96CEB4' },
            { id: 8, nombre: 'Region del Biobio', lat: -36.827, lng: -73.050, color: '#FFEAA7' },
            { id: 9, nombre: 'Region de La Araucania', lat: -38.736, lng: -72.591, color: '#DDA0DD' },
            { id: 10, nombre: 'Region de Los Lagos', lat: -41.469, lng: -72.942, color: '#98D8C8' },
            { id: 13, nombre: 'Region Metropolitana de Santiago', lat: -33.449, lng: -70.669, color: '#F7DC6F' },
            { id: 15, nombre: 'Region de Arica y Parinacota', lat: -18.478, lng: -70.312, color: '#BB8FCE' },
            { id: 16, nombre: 'Region de Nuble', lat: -36.624, lng: -71.957, color: '#85C1E9' }
        ];

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
                    <button class="btn-ver-detalles" data-region-id="${region.id}">
                        Ver Estadisticas
                    </button>
                    <button class="btn-agregar-analisis" data-region-id="${region.id}" data-region-nombre="${region.nombre}">
                        Agregar a Analisis
                    </button>
                </div>
            `);

            marcador.on('popupopen', () => {
                const popup = marcador.getPopup();
                const element = popup.getElement();
                if (element) {
                    element.querySelector('.btn-ver-detalles').addEventListener('click', () => {
                        this.seleccionarRegion(region.id);
                        this.mapa.closePopup();
                    });
                    element.querySelector('.btn-agregar-analisis').addEventListener('click', () => {
                        this.agregarRegionAnalisis(region.id, region.nombre);
                        this.mapa.closePopup();
                    });
                }
            });

            marcador.on('click', () => {
                this.seleccionarRegion(region.id);
            });
        });
    }

    async seleccionarRegion(regionId) {
        try {
            if (!this.marcadoresRegiones[regionId]) {
                console.warn(`Region ${regionId} no esta en el mapa`);
                return;
            }

            this.regionSeleccionada = regionId;
            this.mostrarCargando('info-region', 'Cargando informacion de la region...');
            
            this.resaltarRegionSeleccionada(regionId);
            
            const responseRegion = await fetch(`/api/region/${regionId}/`);
            if (!responseRegion.ok) {
                throw new Error(`Error cargando region: ${responseRegion.status}`);
            }
            
            const dataRegion = await responseRegion.json();
            
            if (dataRegion.error) {
                throw new Error(dataRegion.error);
            }
            
            this.mostrarInfoRegion(dataRegion);
            this.cargarProductosRegion(regionId);
            
        } catch (error) {
            console.error('Error seleccionando region:', error);
            this.mostrarError('info-region', 'Error cargando la region seleccionada');
        }
    }

    resaltarRegionSeleccionada(regionId) {
        Object.values(this.marcadoresRegiones).forEach(marcador => {
            const icon = marcador.getIcon();
            if (icon.options && icon.options.className) {
                marcador.setIcon(L.divIcon({
                    ...icon.options,
                    className: icon.options.className.replace(' selected', '')
                }));
            }
        });

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
        const contenedor = document.getElementById('info-region');
        
        let subsectoresHTML = '';
        if (data.subsectores && data.subsectores.length > 0) {
            subsectoresHTML = data.subsectores.slice(0, 5).map(subsector => {
                const nombreSubsector = subsector.nombre || 'Sin nombre';
                return `<span class="badge">${nombreSubsector} (${subsector.total})</span>`;
            }).join('');
        }

        contenedor.innerHTML = `
            <div class="region-header">
                <h3>${data.region_nombre}</h3>
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
                    <h4>Subsectores principales:</h4>
                    <div class="subsectores-list">
                        ${subsectoresHTML}
                    </div>
                </div>
            ` : ''}
            <div class="botones-region">
                <button class="btn-agregar-analisis-region" onclick="app.agregarRegionAnalisis(${data.region_id}, '${data.region_nombre}')">
                    Agregar a Analisis
                </button>
            </div>
            <div class="productos-section">
                <h4>Productos disponibles:</h4>
                <div id="lista-productos" class="productos-list">
                    <p>Cargando productos...</p>
                </div>
            </div>
        `;
    }

    agregarRegionAnalisis(regionId, regionNombre) {
        try {
            if (this.regionesAnalisis.has(regionId)) {
                this.mostrarMensaje('Esta region ya esta en el analisis', 'info');
                return;
            }

            this.regionesAnalisis.add(regionId);
            this.actualizarListaAnalisis();
            this.mostrarMensaje(`Region "${regionNombre}" agregada al analisis`, 'success');
            
        } catch (error) {
            console.error('Error agregando region al analisis:', error);
            this.mostrarMensaje('Error agregando region al analisis', 'error');
        }
    }

    removerRegionAnalisis(regionId) {
        try {
            this.regionesAnalisis.delete(regionId);
            this.actualizarListaAnalisis();
            this.mostrarMensaje('Region removida del analisis', 'info');
            
        } catch (error) {
            console.error('Error removiendo region del analisis:', error);
            this.mostrarMensaje('Error removiendo region del analisis', 'error');
        }
    }

    actualizarListaAnalisis() {
        const lista = document.getElementById('lista-regiones-analisis');
        const botonComparar = document.getElementById('comparar-regiones');

        if (this.regionesAnalisis.size === 0) {
            lista.innerHTML = '<p class="sin-region-seleccionada">No hay regiones seleccionadas para analisis</p>';
            botonComparar.disabled = true;
            return;
        }

        botonComparar.disabled = false;
        lista.innerHTML = Array.from(this.regionesAnalisis).map(regionId => {
            const region = this.obtenerNombreRegion(regionId);
            return `
                <div class="region-analisis-item">
                    <span>${region}</span>
                    <button class="btn-remover-analisis" onclick="app.removerRegionAnalisis(${regionId})">
                        Quitar
                    </button>
                </div>
            `;
        }).join('');
    }

    obtenerNombreRegion(regionId) {
        const marcador = this.marcadoresRegiones[regionId];
        if (marcador) {
            return marcador.getTooltip()?.getContent() || `Region ${regionId}`;
        }
        return `Region ${regionId}`;
    }

// En la clase MapaInteractivo - REEMPLAZAR la función compararRegiones
async compararRegiones() {
    try {
        if (this.regionesAnalisis.size === 0) {
            this.mostrarMensaje('No hay regiones seleccionadas para comparar', 'error');
            return;
        }

        this.mostrarCargando('info-region', 'Comparando regiones...');
        
        // Construir URL con las regiones seleccionadas
        const regionesIds = Array.from(this.regionesAnalisis).join(',');
        const url = `/api/comparar-regiones/?regiones=${regionesIds}`;
        
        const response = await fetch(url);
        if (!response.ok) {
            throw new Error(`Error HTTP: ${response.status}`);
        }
        
        const data = await response.json();
        
        if (data.error) {
            throw new Error(data.error);
        }
        
        this.mostrarComparacionRegiones(data);
        
    } catch (error) {
        console.error('Error comparando regiones:', error);
        this.mostrarError('info-region', 'Error al comparar regiones');
    }
}

// AGREGAR esta nueva función para mostrar la comparación
mostrarComparacionRegiones(data) {
    const contenedor = document.getElementById('info-region');
    
    if (!data.regiones_comparadas || data.regiones_comparadas.length === 0) {
        contenedor.innerHTML = `
            <div class="error">
                <p>No se pudieron obtener datos para comparar las regiones</p>
            </div>
        `;
        return;
    }

    let comparacionHTML = `
        <div class="comparacion-header">
            <h3>Comparacion de Regiones</h3>
            <p class="texto-pequeno">${data.total_regiones} regiones comparadas</p>
        </div>
        <div class="tabla-comparacion-container">
            <table class="tabla-comparacion">
                <thead>
                    <tr>
                        <th>Region</th>
                        <th>Registros</th>
                        <th>Productos Unicos</th>
                        <th>Mercados</th>
                        <th>Precio Promedio</th>
                        <th>Volumen Total</th>
                    </tr>
                </thead>
                <tbody>
    `;

    data.regiones_comparadas.forEach(region => {
        const estadisticas = region.estadisticas;
        const precioPromedio = estadisticas.precio_promedio ? 
            parseFloat(estadisticas.precio_promedio).toFixed(2) : 'N/A';
        const volumenTotal = estadisticas.volumen_total ? 
            parseFloat(estadisticas.volumen_total).toLocaleString('es-CL') : '0';

        comparacionHTML += `
            <tr>
                <td><strong>${region.region_nombre}</strong></td>
                <td>${estadisticas.total_registros || '0'}</td>
                <td>${estadisticas.productos_unicos || '0'}</td>
                <td>${estadisticas.total_mercados || '0'}</td>
                <td>${precioPromedio !== 'N/A' ? '$' + precioPromedio : precioPromedio}</td>
                <td>${volumenTotal}</td>
            </tr>
        `;
    });

    comparacionHTML += `
                </tbody>
            </table>
        </div>
        <div class="resumen-comparacion">
            <h4>Resumen de Comparacion</h4>
            <div class="metricas-comparacion">
                ${this.generarMetricasComparacion(data.regiones_comparadas)}
            </div>
        </div>
    `;

    contenedor.innerHTML = comparacionHTML;
}

// función para generar métricas de comparación
generarMetricasComparacion(regiones) {
    if (regiones.length < 2) return '<p>Se necesitan al menos 2 regiones para comparar</p>';

    const precios = regiones.map(r => parseFloat(r.estadisticas.precio_promedio) || 0).filter(p => p > 0);
    const volumenes = regiones.map(r => parseFloat(r.estadisticas.volumen_total) || 0);
    
    const regionMayorPrecio = precios.length > 0 ? 
        regiones[precios.indexOf(Math.max(...precios))] : null;
    const regionMenorPrecio = precios.length > 0 ? 
        regiones[precios.indexOf(Math.min(...precios))] : null;
    const regionMayorVolumen = volumenes.length > 0 ? 
        regiones[volumenes.indexOf(Math.max(...volumenes))] : null;

    let metricasHTML = '';

    if (regionMayorPrecio && regionMenorPrecio) {
        const diferenciaPrecio = ((parseFloat(regionMayorPrecio.estadisticas.precio_promedio) - 
                                 parseFloat(regionMenorPrecio.estadisticas.precio_promedio)) / 
                                 parseFloat(regionMenorPrecio.estadisticas.precio_promedio) * 100).toFixed(1);
        
        metricasHTML += `
            <div class="metrica-item">
                <span class="metrica-label">Mayor precio promedio:</span>
                <span class="metrica-valor">${regionMayorPrecio.region_nombre} ($${parseFloat(regionMayorPrecio.estadisticas.precio_promedio).toFixed(2)})</span>
            </div>
            <div class="metrica-item">
                <span class="metrica-label">Menor precio promedio:</span>
                <span class="metrica-valor">${regionMenorPrecio.region_nombre} ($${parseFloat(regionMenorPrecio.estadisticas.precio_promedio).toFixed(2)})</span>
            </div>
            <div class="metrica-item">
                <span class="metrica-label">Diferencia de precio:</span>
                <span class="metrica-valor ${diferenciaPrecio > 0 ? 'positivo' : 'negativo'}">${diferenciaPrecio}%</span>
            </div>
        `;
    }

    if (regionMayorVolumen) {
        metricasHTML += `
            <div class="metrica-item">
                <span class="metrica-label">Mayor volumen total:</span>
                <span class="metrica-valor">${regionMayorVolumen.region_nombre} (${parseFloat(regionMayorVolumen.estadisticas.volumen_total).toLocaleString('es-CL')})</span>
            </div>
        `;
    }

    return metricasHTML || '<p>No hay datos suficientes para generar metricas</p>';
}
    limpiarAnalisis() {
        try {
            this.regionesAnalisis.clear();
            this.actualizarListaAnalisis();
            this.mostrarMensaje('Analisis limpiado', 'info');
            
        } catch (error) {
            console.error('Error limpiando analisis:', error);
            this.mostrarMensaje('Error limpiando analisis', 'error');
        }
    }

    async cargarProductosRegion(regionId) {
        try {
            this.mostrarCargando('lista-productos', 'Cargando productos...');
            
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

    mostrarProductosRegion(data) {
        const contenedor = document.getElementById('lista-productos');
        
        if (!data.productos || data.productos.length === 0) {
            contenedor.innerHTML = `
                <div class="sin-resultados">
                    <p>No se encontraron productos</p>
                    <p class="texto-pequeno">Prueba ajustando los filtros</p>
                </div>
            `;
            return;
        }

        const productosHTML = data.productos.map(producto => {
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
}

// Inicializar la aplicación cuando se carga la página
document.addEventListener('DOMContentLoaded', function() {
    try {
        window.app = new MapaInteractivo();
        console.log('Mapa interactivo inicializado correctamente');
    } catch (error) {
        console.error('Error inicializando el mapa interactivo:', error);
        const errorElement = document.createElement('div');
        errorElement.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            background: #dc3545;
            color: white;
            padding: 20px;
            text-align: center;
            z-index: 10000;
        `;
        errorElement.textContent = 'Error al cargar el mapa interactivo. Por favor, recarga la pagina.';
        document.body.appendChild(errorElement);
    }
});