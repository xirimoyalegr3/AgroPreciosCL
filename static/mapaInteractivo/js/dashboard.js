// static/mapaInteractivo/js/dashboard.js
class DashboardAnalisis {
    constructor(app) {
        this.app = app;
        this.datos = null;
        this.estado = 'cerrado';
        this.filtrosActuales = {};
        this.graficos = {};
        // NO llamar init() aquí - se llamará después de crear la estructura HTML
    }

    init() {
        this.crearEstructuraHTML();
        this.configurarEventListeners();
        console.log('Dashboard inicializado correctamente');
    }

    crearEstructuraHTML() {
        // Verificar si ya existe la estructura para no duplicar
        if (document.getElementById('dashboard-overlay')) {
            console.log('Estructura del dashboard ya existe');
            return;
        }

        // Crear overlay
        const overlay = document.createElement('div');
        overlay.className = 'dashboard-overlay';
        overlay.id = 'dashboard-overlay';

        // Crear contenedor principal
        const container = document.createElement('div');
        container.className = 'dashboard-container';
        container.id = 'dashboard-container';

        container.innerHTML = `
            <div class="dashboard-header">
                <h2>Dashboard de Análisis de Negocios</h2>
                <div class="dashboard-controls">
                    <button class="btn-dashboard-control" id="cerrar-dashboard">×</button>
                </div>
            </div>
            <div class="dashboard-content" id="dashboard-content">
                <div class="dashboard-loading">
                    <p>Cargando análisis de negocios...</p>
                </div>
            </div>
        `;

        // Crear botón flotante
        const botonFlotante = document.createElement('button');
        botonFlotante.className = 'btn-dashboard-flotante';
        botonFlotante.id = 'abrir-dashboard';
        botonFlotante.innerHTML = '';
        botonFlotante.title = 'Abrir Dashboard de Análisis';

        document.body.appendChild(overlay);
        document.body.appendChild(container);
        document.body.appendChild(botonFlotante);

        console.log('Estructura HTML del dashboard creada');
    }

    configurarEventListeners() {
        // Botón abrir dashboard
        const botonAbrir = document.getElementById('abrir-dashboard');
        if (!botonAbrir) {
            console.error('Botón abrir-dashboard no encontrado');
            return;
        }

        botonAbrir.addEventListener('click', () => {
            this.abrir();
        });

        // Controles del dashboard
        const botonMinimizar = document.getElementById('minimizar-dashboard');
        const botonCerrar = document.getElementById('cerrar-dashboard');

        if (botonMinimizar) {
            botonMinimizar.addEventListener('click', () => {
                this.minimizar();
            });
        }

        if (botonCerrar) {
            botonCerrar.addEventListener('click', () => {
                this.cerrar();
            });
        }

        // Cerrar con overlay
        const overlay = document.getElementById('dashboard-overlay');
        if (overlay) {
            overlay.addEventListener('click', (e) => {
                if (e.target.id === 'dashboard-overlay') {
                    this.cerrar();
                }
            });
        }

        console.log('Event listeners del dashboard configurados');
    }

 async abrir() {
        this.estado = 'abierto';
        document.getElementById('dashboard-overlay').style.display = 'block';
        document.getElementById('dashboard-container').style.display = 'block';
        document.getElementById('dashboard-container').classList.remove('dashboard-minimized');

        // Cargar datos con los filtros actuales de la app
        await this.cargarDatosDashboard(this.app.filtros);
    }


    minimizar() {
        if (this.estado === 'minimizado') {
            this.abrir();
        } else {
            this.estado = 'minimizado';
            document.getElementById('dashboard-container').classList.add('dashboard-minimized');
        }
    }

    cerrar() {
        this.estado = 'cerrado';
        document.getElementById('dashboard-overlay').style.display = 'none';
        document.getElementById('dashboard-container').style.display = 'none';
    }


async cargarDatosDashboard(filtros = {}) {
    try {
        this.filtrosActuales = filtros;

        // Mostrar loading con información de filtros
        const content = document.getElementById('dashboard-content');
        let mensajeLoading = 'Cargando análisis de negocios...';

        if (Object.keys(filtros).length > 0) {
            const filtrosTexto = Object.entries(filtros)
                .filter(([key, value]) => value && value !== '')
                .map(([key, value]) => `${key}: ${value}`)
                .join(', ');

            if (filtrosTexto) {
                mensajeLoading += ` (Filtros: ${filtrosTexto})`;
            }
        }

        content.innerHTML = `
            <div class="dashboard-loading">
                <p>${mensajeLoading}</p>
                <div style="margin-top: 10px; font-size: 0.9em; color: #6c757d;">
                    <p> Sincronizando con el mapa...</p>
                </div>
            </div>
        `;

        // Construir URL con filtros
        const params = new URLSearchParams();
        Object.entries(filtros).forEach(([key, value]) => {
            if (value && value !== '') {
                params.append(key, value);
            }
        });

        const url = `/api/dashboard-analisis/?${params.toString()}`;
        console.log('Cargando dashboard desde:', url);

        const response = await fetch(url, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
            },
            timeout: 15000
        });

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }

        this.datos = await response.json();

        // Verificar si hay datos después de aplicar filtros
        if (this.datos.metricas_principales && this.datos.metricas_principales.total_registros_filtrados === 0) {
            this.mostrarMensaje('No hay datos que coincidan con los filtros aplicados. Intenta con otros criterios.', 'info');
        } else {
            this.mostrarMensaje('Dashboard actualizado con los filtros actuales', 'success');
        }

        this.mostrarDashboard();

    } catch (error) {
        console.error('Error cargando dashboard con filtros:', error);

        // Usar datos de ejemplo como fallback
        this.datos = this.generarDatosEjemplo();
        this.datos.filtros_aplicados = filtros;
        this.mostrarDashboard();
        this.mostrarMensaje('Usando datos de ejemplo - La API no está disponible temporalmente', 'warning');
    }
}

    // DATOS DE EJEMPLO ROBUSTOS
    generarDatosEjemplo() {
        return {
            metricas_principales: {
                margen_potencial_promedio: 42.3,
                productos_alto_margen: 12,
                regiones_activas: 7,
                estacionalidad_promedio: 35.8
            },
            analisis_precios: {
                top_oportunidades: [
                    {
                        producto: 'Palta Hass',
                        mejor_region: 'RM Santiago',
                        peor_region: 'Valparaíso',
                        precio_maximo: '$4.2K',
                        precio_minimo: '$2.8K',
                        diferencial_precio: '$1.4K',
                        margen_potencial: 50.0
                    },
                    {
                        producto: 'Tomate',
                        mejor_region: 'RM Santiago',
                        peor_region: 'Maule',
                        precio_maximo: '$1.8K',
                        precio_minimo: '$1.2K',
                        diferencial_precio: '$600',
                        margen_potencial: 50.0
                    },
                    {
                        producto: 'Naranjas',
                        mejor_region: 'RM Santiago',
                        peor_region: 'Coquimbo',
                        precio_maximo: '$1.5K',
                        precio_minimo: '$900',
                        diferencial_precio: '$600',
                        margen_potencial: 66.7
                    },
                    {
                        producto: 'Cebollas',
                        mejor_region: 'Biobío',
                        peor_region: 'Maule',
                        precio_maximo: '$800',
                        precio_minimo: '$500',
                        diferencial_precio: '$300',
                        margen_potencial: 60.0
                    },
                    {
                        producto: 'Zanahorias',
                        mejor_region: 'RM Santiago',
                        peor_region: 'La Araucanía',
                        precio_maximo: '$700',
                        precio_minimo: '$450',
                        diferencial_precio: '$250',
                        margen_potencial: 55.6
                    }
                ]
            },
            analisis_volumenes: {
                top_regiones_volumen: [
                    {
                        region: 'RM Santiago',
                        producto_mas_transado: 'Tomate',
                        volumen_total: '2.3M',
                        mercados_activos: 5,
                        liquidez: 12.5
                    },
                    {
                        region: 'Región del Maule',
                        producto_mas_transado: 'Cebolla',
                        volumen_total: '1.8M',
                        mercados_activos: 3,
                        liquidez: 8.2
                    },
                    {
                        region: 'Región de Coquimbo',
                        producto_mas_transado: 'Uva',
                        volumen_total: '1.2M',
                        mercados_activos: 2,
                        liquidez: 6.8
                    },
                    {
                        region: 'Región del Biobío',
                        producto_mas_transado: 'Manzana',
                        volumen_total: '950K',
                        mercados_activos: 3,
                        liquidez: 7.1
                    },
                    {
                        region: 'Región de Valparaíso',
                        producto_mas_transado: 'Palta',
                        volumen_total: '780K',
                        mercados_activos: 2,
                        liquidez: 5.4
                    }
                ]
            },
            oportunidades_mercado: [
                {
                    tipo: 'Arbitraje Regional',
                    descripcion: 'Palta Hass - Variación 50.0%',
                    potencial: 'Alto',
                    riesgo: 'Medio',
                    recomendacion: 'Comprar en Valparaíso, vender en RM Santiago'
                },
                {
                    tipo: 'Mercado Estable',
                    descripcion: 'Tomate en RM Santiago',
                    potencial: 'Medio',
                    riesgo: 'Bajo',
                    recomendacion: 'Mercado estable con buena relación precio-volumen'
                },
                {
                    tipo: 'Producto Estacional',
                    descripcion: 'Naranjas en invierno',
                    potencial: 'Alto',
                    riesgo: 'Bajo',
                    recomendacion: 'Almacenar en temporada baja para vender en alta'
                },
                {
                    tipo: 'Mercado Emergente',
                    descripcion: 'Berries en La Araucanía',
                    potencial: 'Medio',
                    riesgo: 'Alto',
                    recomendacion: 'Evaluar mercado antes de invertir'
                }
            ],
            analisis_temporal: {
                estacionalidad_productos: [
                    {
                        producto: 'Palta Hass',
                        mejor_mes_comprar: 'Enero',
                        mejor_mes_vender: 'Junio',
                        variacion_estacional: 45.2,
                        tendencia: 'Alcista'
                    },
                    {
                        producto: 'Tomate',
                        mejor_mes_comprar: 'Marzo',
                        mejor_mes_vender: 'Agosto',
                        variacion_estacional: 32.1,
                        tendencia: 'Estable'
                    },
                    {
                        producto: 'Naranja',
                        mejor_mes_comprar: 'Mayo',
                        mejor_mes_vender: 'Noviembre',
                        variacion_estacional: 28.7,
                        tendencia: 'Alcista'
                    },
                    {
                        producto: 'Uva',
                        mejor_mes_comprar: 'Febrero',
                        mejor_mes_vender: 'Diciembre',
                        variacion_estacional: 38.9,
                        tendencia: 'Alcista'
                    },
                    {
                        producto: 'Manzana',
                        mejor_mes_comprar: 'Abril',
                        mejor_mes_vender: 'Septiembre',
                        variacion_estacional: 25.4,
                        tendencia: 'Estable'
                    }
                ]
            }
        };
    }


generarSeccionesContextuales(tipoAnalisis) {
    let seccionesEspecificas = '';

    // Agregar secciones específicas según el tipo de análisis
    if (tipoAnalisis === 'region_especifica') {
        seccionesEspecificas = this.generarSeccionesRegional();
    } else if (tipoAnalisis === 'producto_especifico') {
        seccionesEspecificas = this.generarSeccionesProducto();
    } else {
        seccionesEspecificas = this.generarSeccionesGenerales();
    }

    return seccionesEspecificas;
}
//   Crear gráfico de precios temporales
async crearGraficoPreciosTemporales(containerId) {
    try {
        const params = new URLSearchParams();
        Object.entries(this.filtrosActuales).forEach(([key, value]) => {
            if (value && value !== '') {
                params.append(key, value);
            }
        });

        const response = await fetch(`/api/graficos/precios-temporales/?${params.toString()}`);
        const data = await response.json();

        if (data.error) {
            throw new Error(data.error);
        }

        const ctx = document.getElementById(containerId).getContext('2d');

        // Destruir gráfico anterior si existe
        if (this.graficos[containerId]) {
            this.graficos[containerId].destroy();
        }

        this.graficos[containerId] = new Chart(ctx, {
            type: 'line',
            data: data,
            options: {
                responsive: true,
                plugins: {
                    title: {
                        display: true,
                        text: 'Evolución de Precios en el Tiempo'
                    },
                    tooltip: {
                        mode: 'index',
                        intersect: false
                    }
                },
                scales: {
                    x: {
                        display: true,
                        title: {
                            display: true,
                            text: 'Fecha'
                        }
                    },
                    y: {
                        display: true,
                        title: {
                            display: true,
                            text: 'Precio ($)'
                        }
                    }
                }
            }
        });

    } catch (error) {
        console.error('Error creando gráfico de precios:', error);
        document.getElementById(containerId).parentElement.innerHTML =
            '<p class="metrica-sin-datos">No se pudieron cargar los datos del gráfico</p>';
    }
}

//   Crear gráfico de distribución por regiones
async crearGraficoDistribucionRegiones(containerId) {
    try {
        const params = new URLSearchParams();
        Object.entries(this.filtrosActuales).forEach(([key, value]) => {
            if (value && value !== '' && key !== 'region_id') { // Excluir region_id para ver todas las regiones
                params.append(key, value);
            }
        });

        const response = await fetch(`/api/graficos/distribucion-regiones/?${params.toString()}`);
        const data = await response.json();

        if (data.error) {
            throw new Error(data.error);
        }

        const ctx = document.getElementById(containerId).getContext('2d');

        if (this.graficos[containerId]) {
            this.graficos[containerId].destroy();
        }

        this.graficos[containerId] = new Chart(ctx, {
            type: 'bar',
            data: data,
            options: {
                responsive: true,
                plugins: {
                    title: {
                        display: true,
                        text: 'Distribución por Regiones'
                    }
                },
                scales: {
                    x: {
                        display: true,
                        title: {
                            display: true,
                            text: 'Regiones'
                        }
                    },
                    y: {
                        display: true,
                        title: {
                            display: true,
                            text: 'Volumen'
                        }
                    },
                    y1: {
                        display: true,
                        position: 'right',
                        title: {
                            display: true,
                            text: 'Precio Promedio ($)'
                        },
                        grid: {
                            drawOnChartArea: false
                        }
                    }
                }
            }
        });

    } catch (error) {
        console.error('Error creando gráfico de distribución:', error);
        document.getElementById(containerId).parentElement.innerHTML =
            '<p class="metrica-sin-datos">No se pudieron cargar los datos del gráfico</p>';
    }
}

//   Crear gráfico de estacionalidad
async crearGraficoEstacionalidad(containerId) {
    try {
        const params = new URLSearchParams();
        Object.entries(this.filtrosActuales).forEach(([key, value]) => {
            if (value && value !== '') {
                params.append(key, value);
            }
        });

        const response = await fetch(`/api/graficos/estacionalidad/?${params.toString()}`);
        const data = await response.json();

        if (data.error) {
            throw new Error(data.error);
        }

        const ctx = document.getElementById(containerId).getContext('2d');

        if (this.graficos[containerId]) {
            this.graficos[containerId].destroy();
        }

        this.graficos[containerId] = new Chart(ctx, {
            type: 'line',
            data: data,
            options: {
                responsive: true,
                plugins: {
                    title: {
                        display: true,
                        text: 'Estacionalidad Anual'
                    }
                },
                scales: {
                    x: {
                        display: true,
                        title: {
                            display: true,
                            text: 'Mes'
                        }
                    },
                    y: {
                        display: true,
                        title: {
                            display: true,
                            text: 'Precio Promedio ($)'
                        }
                    },
                    y1: {
                        display: true,
                        position: 'right',
                        title: {
                            display: true,
                            text: 'Volumen Promedio'
                        },
                        grid: {
                            drawOnChartArea: false
                        }
                    }
                }
            }
        });

    } catch (error) {
        console.error('Error creando gráfico de estacionalidad:', error);
        document.getElementById(containerId).parentElement.innerHTML =
            '<p class="metrica-sin-datos">No se pudieron cargar los datos del gráfico</p>';
    }
}
generarSeccionesRegional() {
    return `
        <!-- ANÁLISIS DE MERCADOS EN LA REGIÓN -->
        <div class="dashboard-section">
            <h3>Mercados en la Región</h3>
            ${this.generarAnalisisMercadosRegional()}
        </div>

        <!-- SECCIÓN 3: ANÁLISIS DE VOLÚMENES -->
        <div class="dashboard-section">
            <h3>Productos Más Transados</h3>
            ${this.generarAnalisisVolumenes()}
        </div>

        <!-- SECCIÓN 4: OPORTUNIDADES DE MERCADO -->
        <div class="dashboard-section">
            <h3>Oportunidades Locales</h3>
            ${this.generarOportunidadesMercado()}
        </div>

        <!-- SECCIÓN 5: TENDENCIAS TEMPORALES -->
        <div class="dashboard-section">
            <h3>Estacionalidad en la Región</h3>
            ${this.generarAnalisisTemporal()}
        </div>

        <!-- BOTONES DE EXPORTACIÓN -->
        <div class="botones-exportacion">
            <button class="btn-exportar btn-exportar-pdf">Exportar a PDF</button>
            <button class="btn-exportar btn-exportar-excel">Exportar a Excel</button>
        </div>
    `;
}

obtenerDescripcionTipoAnalisis(tipo) {
    const descripciones = {
        'region_especifica': 'Análisis detallado de la región seleccionada',
        'producto_especifico': 'Análisis del producto en todas las regiones',
        'subsector_especifico': 'Análisis del subsector a nivel nacional',
        'producto_region_especifica': 'Análisis específico del producto en la región',
        'general': 'Vista general nacional'
    };
    return descripciones[tipo] || 'Análisis general';
}


    generarSeccionesRestantes() {
        return `
            <!-- SECCIÓN 2: ANÁLISIS DE PRECIOS -->
            <div class="dashboard-section">
                <h3>Analisis de Precios por Region</h3>
                ${this.generarAnalisisPrecios()}
            </div>

            <!-- SECCIÓN 3: ANÁLISIS DE VOLÚMENES -->
            <div class="dashboard-section">
                <h3>Analisis de Volumenes Comerciales</h3>
                ${this.generarAnalisisVolumenes()}
            </div>

            <!-- SECCIÓN 4: OPORTUNIDADES DE MERCADO -->
            <div class="dashboard-section">
                <h3>Oportunidades de Negocio</h3>
                ${this.generarOportunidadesMercado()}
            </div>

            <!-- SECCIÓN 5: TENDENCIAS TEMPORALES -->
            <div class="dashboard-section">
                <h3>Analisis Temporal</h3>
                ${this.generarAnalisisTemporal()}
            </div>

            <!-- BOTONES DE EXPORTACIÓN -->
            <div class="botones-exportacion">
                <button class="btn-exportar btn-exportar-pdf">Exportar a PDF</button>
                <button class="btn-exportar btn-exportar-excel">Exportar a Excel</button>
            </div>
        `;
    }

generarMetricasPrincipales() {
        if (!this.datos || !this.datos.metricas_principales) {
            return '<p class="metrica-sin-datos">No hay datos disponibles</p>';
        }

        const metricas = this.datos.metricas_principales;

        // Mostrar total de registros filtrados si está disponible
        const totalRegistros = metricas.total_registros_filtrados !== undefined ?
            metricas.total_registros_filtrados : 0;

        const crearMetricaCard = (valor, label, esPorcentaje = false) => {
            const mostrarValor = valor === 'N/A' || valor === 0 || valor === null || valor === undefined;
            const valorFormateado = mostrarValor ?
                'N/D' :
                (esPorcentaje ? `${valor}%` : valor.toLocaleString('es-CL'));

            const claseValor = mostrarValor ? 'metrica-sin-datos' : 'metrica-valor';

            return `
                <div class="metrica-card">
                    <span class="${claseValor}">${valorFormateado}</span>
                    <span class="metrica-label">${label}</span>
                </div>
            `;
        };

        return `
            ${crearMetricaCard(totalRegistros, 'Registros (filtrados)')}
            ${crearMetricaCard(metricas.margen_potencial_promedio, 'Margen Potencial Promedio', true)}
            ${crearMetricaCard(metricas.productos_alto_margen, 'Productos con Alto Margen')}
            ${crearMetricaCard(metricas.regiones_activas, 'Regiones Activas')}
            ${crearMetricaCard(metricas.estacionalidad_promedio, 'Estacionalidad Promedio', true)}
        `;
    }


    generarAnalisisPrecios() {
        if (!this.datos || !this.datos.analisis_precios || !this.datos.analisis_precios.top_oportunidades) {
            return '<p class="metrica-sin-datos">No hay datos de análisis de precios</p>';
        }

        const analisis = this.datos.analisis_precios;

        if (analisis.top_oportunidades.length === 0) {
            return '<p class="metrica-sin-datos">No se encontraron oportunidades de precio</p>';
        }

        return `
            <div class="tabla-container">
                <table class="tabla-analisis">
                    <thead>
                        <tr>
                            <th>Producto</th>
                            <th>Mejor Región</th>
                            <th>Precio Max</th>
                            <th>Peor Región</th>
                            <th>Precio Min</th>
                            <th>Diferencial</th>
                            <th>Margen</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${analisis.top_oportunidades.map(oportunidad => `
                            <tr>
                                <td><strong>${oportunidad.producto}</strong></td>
                                <td>${oportunidad.mejor_region}</td>
                                <td class="precio-formateado">${oportunidad.precio_maximo}</td>
                                <td>${oportunidad.peor_region}</td>
                                <td class="precio-formateado">${oportunidad.precio_minimo}</td>
                                <td class="precio-formateado">${oportunidad.diferencial_precio}</td>
                                <td class="tendencia-positiva">${oportunidad.margen_potencial}%</td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            </div>
        `;
    }

    generarAnalisisVolumenes() {
        if (!this.datos || !this.datos.analisis_volumenes || !this.datos.analisis_volumenes.top_regiones_volumen) {
            return '<p class="metrica-sin-datos">No hay datos de análisis de volúmenes</p>';
        }

        const analisis = this.datos.analisis_volumenes;

        if (analisis.top_regiones_volumen.length === 0) {
            return '<p class="metrica-sin-datos">No hay datos de volúmenes por región</p>';
        }

        return `
            <div class="tabla-container">
                <table class="tabla-analisis">
                    <thead>
                        <tr>
                            <th>Región</th>
                            <th>Producto Principal</th>
                            <th>Volumen Total</th>
                            <th>Mercados</th>
                            <th>Liquidez</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${analisis.top_regiones_volumen.map(region => `
                            <tr>
                                <td><strong>${region.region}</strong></td>
                                <td>${region.producto_mas_transado}</td>
                                <td class="precio-formateado">${region.volumen_total}</td>
                                <td>${region.mercados_activos}</td>
                                <td class="tendencia-positiva">${region.liquidez}</td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            </div>
        `;
    }

    generarOportunidadesMercado() {
        if (!this.datos || !this.datos.oportunidades_mercado) {
            return '<p class="metrica-sin-datos">No hay datos de oportunidades</p>';
        }

        const oportunidades = this.datos.oportunidades_mercado;

        if (oportunidades.length === 0) {
            return '<p class="metrica-sin-datos">No se identificaron oportunidades</p>';
        }

        const getBadgeClass = (nivel) => {
            switch(nivel) {
                case 'Alto': return 'badge-potencial';
                case 'Medio': return 'badge-medio';
                case 'Bajo': return 'badge-bajo';
                default: return 'badge-medio';
            }
        };

        return `
            <div class="tabla-container">
                <table class="tabla-analisis">
                    <thead>
                        <tr>
                            <th>Tipo</th>
                            <th>Descripción</th>
                            <th>Potencial</th>
                            <th>Riesgo</th>
                            <th>Recomendación</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${oportunidades.map(oportunidad => `
                            <tr>
                                <td><strong>${oportunidad.tipo}</strong></td>
                                <td>${oportunidad.descripcion}</td>
                                <td><span class="${getBadgeClass(oportunidad.potencial)}">${oportunidad.potencial}</span></td>
                                <td><span class="${getBadgeClass(oportunidad.riesgo)}">${oportunidad.riesgo}</span></td>
                                <td style="max-width: 200px; white-space: normal;">${oportunidad.recomendacion}</td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            </div>
        `;
    }
//   Configurar interactividad en gráficos
configurarInteractividadGraficos() {
    // Interactividad en gráfico de distribución regional
    if (this.graficos['grafico-distribucion-regiones']) {
        const chart = this.graficos['grafico-distribucion-regiones'];

        chart.canvas.onclick = (evt) => {
            const points = chart.getElementsAtEventForMode(evt, 'nearest', { intersect: true }, true);

            if (points.length > 0) {
                const firstPoint = points[0];
                const regionNombre = chart.data.labels[firstPoint.index];

                // Buscar el ID de la región por nombre
                this.seleccionarRegionDesdeDashboard(regionNombre);
            }
        };

        // Cambiar cursor al hover
        chart.canvas.style.cursor = 'pointer';
    }

    // Interactividad en gráfico de precios temporales
    if (this.graficos['grafico-precios-temporales']) {
        const chart = this.graficos['grafico-precios-temporales'];

        chart.canvas.onclick = (evt) => {
            const points = chart.getElementsAtEventForMode(evt, 'nearest', { intersect: true }, true);

            if (points.length > 0) {
                const firstPoint = points[0];
                const fechaLabel = chart.data.labels[firstPoint.index];

                // Extraer año y mes del label
                this.filtrarPorFechaDesdeDashboard(fechaLabel);
            }
        };

        chart.canvas.style.cursor = 'pointer';
    }
}

//   Seleccionar región desde el dashboard
seleccionarRegionDesdeDashboard(regionNombre) {
    if (!this.app || !this.app.mapa) return;

    console.log('Seleccionando región desde dashboard:', regionNombre);

    // Buscar la región por nombre en los marcadores
    let regionId = null;
    Object.entries(this.app.marcadoresRegiones).forEach(([id, marcador]) => {
        const tooltipContent = marcador.getTooltip()?.getContent();
        if (tooltipContent && tooltipContent.includes(regionNombre)) {
            regionId = parseInt(id);
        }
    });

    if (regionId) {
        // Seleccionar la región en el mapa
        this.app.seleccionarRegion(regionId);

        // Centrar el mapa en la región
        const marcador = this.app.marcadoresRegiones[regionId];
        if (marcador) {
            this.app.mapa.setView(marcador.getLatLng(), 8);
        }

        this.mostrarMensaje(`Centrado en ${regionNombre}`, 'info');
    } else {
        this.mostrarMensaje(`No se pudo encontrar la región: ${regionNombre}`, 'warning');
    }
}

//   Filtrar por fecha desde dashboard
filtrarPorFechaDesdeDashboard(fechaLabel) {
    if (!this.app) return;

    console.log('Filtrando por fecha desde dashboard:', fechaLabel);

    // Extraer año del formato "mes/año"
    const partes = fechaLabel.split('/');
    if (partes.length === 2) {
        const año = partes[1];

        // Aplicar filtro de año en el mapa
        const selectAno = document.getElementById('filtro-año');
        if (selectAno) {
            selectAno.value = año;
            this.app.aplicarFiltros();
        }

        this.mostrarMensaje(`Filtrado por año: ${año}`, 'info');
    }
}
    generarAnalisisTemporal() {
        if (!this.datos || !this.datos.analisis_temporal || !this.datos.analisis_temporal.estacionalidad_productos) {
            return '<p class="metrica-sin-datos">No hay datos de análisis temporal</p>';
        }

        const temporal = this.datos.analisis_temporal;

        if (temporal.estacionalidad_productos.length === 0) {
            return '<p class="metrica-sin-datos">No hay datos de estacionalidad</p>';
        }

        return `
            <div class="tabla-container">
                <table class="tabla-analisis">
                    <thead>
                        <tr>
                            <th>Producto</th>
                            <th>Mejor Comprar</th>
                            <th>Mejor Vender</th>
                            <th>Variación</th>
                            <th>Tendencia</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${temporal.estacionalidad_productos.map(producto => {
                            const claseTendencia = producto.tendencia === 'Alcista' ? 'tendencia-positiva' :
                                                producto.tendencia === 'Estable' ? 'tendencia-estable' : 'tendencia-negativa';
                            return `
                                <tr>
                                    <td><strong>${producto.producto}</strong></td>
                                    <td>${producto.mejor_mes_comprar}</td>
                                    <td>${producto.mejor_mes_vender}</td>
                                    <td>${producto.variacion_estacional}%</td>
                                    <td class="${claseTendencia}">${producto.tendencia}</td>
                                </tr>
                            `;
                        }).join('')}
                    </tbody>
                </table>
            </div>
        `;
    }

exportarPDF() {
    try {
        this.mostrarMensaje('Generando reporte PDF...', 'info');
        
        //  CONSTRUIR URL CON FILTROS ACTUALES
        const params = new URLSearchParams();
        Object.entries(this.filtrosActuales).forEach(([key, value]) => {
            if (value && value !== '') {
                params.append(key, value);
            }
        });
        
        console.log(` Exportando PDF con filtros: ${params.toString()}`);
        
        const link = document.createElement('a');
        link.href = `/api/exportar-pdf/?${params.toString()}`;
        link.download = 'reporte_agroprecios.pdf';
        link.style.display = 'none';
        
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        
        this.mostrarMensaje('Reporte PDF generado correctamente', 'success');
        
    } catch (error) {
        console.error('Error exportando a PDF:', error);
        this.mostrarMensaje('Error al generar el PDF', 'error');
    }
}

exportarExcel() {
    try {
        this.mostrarMensaje('Generando reporte Excel...', 'info');
        
        //  CONSTRUIR URL CON FILTROS ACTUALES
        const params = new URLSearchParams();
        Object.entries(this.filtrosActuales).forEach(([key, value]) => {
            if (value && value !== '') {
                params.append(key, value);
            }
        });
        
        console.log(` Exportando Excel con filtros: ${params.toString()}`);
        
        const link = document.createElement('a');
        link.href = `/api/exportar-excel/?${params.toString()}`;
        link.download = 'reporte_agroprecios.xlsx';
        link.style.display = 'none';
        
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        
        this.mostrarMensaje('Reporte Excel generado correctamente', 'success');
        
    } catch (error) {
        console.error('Error exportando a Excel:', error);
        this.mostrarMensaje('Error al generar el Excel', 'error');
    }
}
//   Secciones para análisis general
generarSeccionesGenerales() {
    return `
        <!-- SECCIÓN 2: ANÁLISIS DE PRECIOS -->
        <div class="dashboard-section">
            <h3>Análisis de Precios por Región</h3>
            ${this.generarAnalisisPrecios()}
        </div>

        <!-- SECCIÓN 3: ANÁLISIS DE VOLÚMENES -->
        <div class="dashboard-section">
            <h3>Análisis de Volúmenes Comerciales</h3>
            ${this.generarAnalisisVolumenes()}
        </div>

        <!-- SECCIÓN 4: OPORTUNIDADES DE MERCADO -->
        <div class="dashboard-section">
            <h3>Oportunidades de Negocio</h3>
            ${this.generarOportunidadesMercado()}
        </div>

        <!-- SECCIÓN 5: TENDENCIAS TEMPORALES -->
        <div class="dashboard-section">
            <h3>Análisis Temporal</h3>
            ${this.generarAnalisisTemporal()}
        </div>

        <!-- BOTONES DE EXPORTACIÓN -->
        <div class="botones-exportacion">
            <button class="btn-exportar btn-exportar-pdf">Exportar a PDF</button>
            <button class="btn-exportar btn-exportar-excel">Exportar a Excel</button>
        </div>
    `;
}

//   Secciones para análisis de producto
generarSeccionesProducto() {
    return `
        <!-- SECCIÓN 2: ANÁLISIS DE PRECIOS -->
        <div class="dashboard-section">
            <h3>Precios del Producto por Región</h3>
            ${this.generarAnalisisPrecios()}
        </div>

        <!-- SECCIÓN 3: ANÁLISIS DE VOLÚMENES -->
        <div class="dashboard-section">
            <h3>Volumen Comercial del Producto</h3>
            ${this.generarAnalisisVolumenes()}
        </div>

        <!-- SECCIÓN 4: OPORTUNIDADES DE MERCADO -->
        <div class="dashboard-section">
            <h3>Oportunidades para el Producto</h3>
            ${this.generarOportunidadesMercado()}
        </div>

        <!-- SECCIÓN 5: TENDENCIAS TEMPORALES -->
        <div class="dashboard-section">
            <h3>Estacionalidad del Producto</h3>
            ${this.generarAnalisisTemporal()}
        </div>

        <!-- BOTONES DE EXPORTACIÓN -->
        <div class="botones-exportacion">
            <button class="btn-exportar btn-exportar-pdf">Exportar a PDF</button>
            <button class="btn-exportar btn-exportar-excel">Exportar a Excel</button>
        </div>
    `;
}

//   Análisis de mercados regional (placeholder por ahora)
generarAnalisisMercadosRegional() {
    if (this.datos.analisis_volumenes && this.datos.analisis_volumenes.mercados_activos) {
        const mercados = this.datos.analisis_volumenes.mercados_activos;

        if (mercados.length > 0) {
            return `
                <div class="tabla-container">
                    <table class="tabla-analisis">
                        <thead>
                            <tr>
                                <th>Mercado</th>
                                <th>Volumen Total</th>
                                <th>Productos Únicos</th>
                                <th>Registros</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${mercados.map(mercado => `
                                <tr>
                                    <td><strong>${mercado.mercado__nombre || 'N/A'}</strong></td>
                                    <td>${mercado.volumen_total ? mercado.volumen_total.toLocaleString('es-CL') : '0'}</td>
                                    <td>${mercado.productos_unicos || '0'}</td>
                                    <td>${mercado.total_registros || '0'}</td>
                                </tr>
                            `).join('')}
                        </tbody>
                    </table>
                </div>
            `;
        }
    }

    return '<p class="metrica-sin-datos">No hay datos de mercados disponibles</p>';
}

//   La función generarSeccionesContextuales para incluir todos los casos
generarSeccionesContextuales(tipoAnalisis) {
    switch(tipoAnalisis) {
        case 'region_especifica':
            return this.generarSeccionesRegional();
        case 'producto_especifico':
            return this.generarSeccionesProducto();
        case 'subsector_especifico':
            return this.generarSeccionesGenerales(); // Usar general por ahora
        case 'producto_region_especifica':
            return this.generarSeccionesRegional(); // Similar a regional
        default:
            return this.generarSeccionesGenerales();
    }
}

//   La función configurarEventListenersExportacion para que esté disponible
configurarEventListenersExportacion() {
    setTimeout(() => {
        const btnPdf = document.querySelector('.btn-exportar-pdf');
        const btnExcel = document.querySelector('.btn-exportar-excel');

        if (btnPdf) {
            btnPdf.addEventListener('click', () => this.exportarPDF());
        }
        if (btnExcel) {
            btnExcel.addEventListener('click', () => this.exportarExcel());
        }
    }, 100);
}


//   En mostrarDashboard, agregar controles de integración
mostrarDashboard() {
    const content = document.getElementById('dashboard-content');

    let headerFiltros = '';
    if (this.datos.filtros_aplicados && Object.keys(this.datos.filtros_aplicados).some(key => this.datos.filtros_aplicados[key])) {
        const filtrosActivos = Object.entries(this.datos.filtros_aplicados)
            .filter(([key, value]) => value && value !== '')
            .map(([key, value]) => `<span class="badge">${key}: ${value}</span>`)
            .join('');

        headerFiltros = `
            <div style="margin-bottom: 20px; padding: 10px; background: #e7f3ff; border-radius: 6px; border: 1px solid #b3d9ff;">
                <strong>Filtros aplicados:</strong>
                <div style="margin-top: 5px;">${filtrosActivos}</div>
            </div>
        `;
    }

    const tituloContextual = this.datos.titulo_contextual || 'Dashboard de Análisis';
    const tipoAnalisis = this.datos.tipo_analisis || 'general';

    // Controles de integración
    const controlesIntegracion = `
        <div style="margin-bottom: 20px; padding: 15px; background: #f8f9fa; border-radius: 8px; border: 1px solid #e9ecef;">
            <h4 style="margin-bottom: 10px; color: #2e7d32;">Controles de Integración</h4>
            <div style="display: flex; gap: 10px; flex-wrap: wrap;">
                <button class="btn-integracion" onclick="dashboard.centrarMapaEnSeleccion()">
                    <i></i> Centrar Mapa
                </button>
                <button class="btn-integracion" onclick="dashboard.limpiarFiltrosDesdeDashboard()">
                    <i></i> Limpiar Filtros
                </button>
            </div>
            <p style="margin-top: 10px; font-size: 0.8em; color: #6c757d;">
                <strong>Tip:</strong> Haz clic en las barras del gráfico de regiones para seleccionarlas en el mapa
            </p>
        </div>
    `;

    content.innerHTML = `
        <div style="margin-bottom: 20px;">
            <h2 style="color: #2e7d32; margin-bottom: 10px;">${tituloContextual}</h2>
            <p style="color: #6c757d; font-size: 0.9em;">Tipo de análisis: ${this.obtenerDescripcionTipoAnalisis(tipoAnalisis)}</p>
        </div>

        ${headerFiltros}
        ${controlesIntegracion}

        <!-- SECCIÓN 1: MÉTRICAS PRINCIPALES -->
        <div class="dashboard-section">
            <h3>Métricas Clave</h3>
            <div class="metricas-grid">
                ${this.generarMetricasPrincipales()}
            </div>
        </div>

        <!-- SECCIÓN: GRÁFICOS PRINCIPALES -->
        <div class="dashboard-section">
            <h3>Visualizaciones Interactivas</h3>
            <div class="graficos-grid">
                <div class="chart-container">
                    <canvas id="grafico-precios-temporales"></canvas>
                </div>
                <div class="chart-container">
                    <canvas id="grafico-distribucion-regiones"></canvas>
                </div>
                <div class="chart-container">
                    <canvas id="grafico-estacionalidad"></canvas>
                </div>
            </div>
        </div>

        ${this.generarSeccionesContextuales(tipoAnalisis)}
    `;

    this.configurarEventListenersExportacion();

    // Cargar gráficos después de que el DOM esté listo
    setTimeout(() => {
        this.cargarGraficos();
    }, 500);
}

//Controles de integración
sincronizarConMapa() {
    if (!this.app) return;

    // Forzar actualización del dashboard con los filtros actuales del mapa
    this.cargarDatosDashboard(this.app.filtros);
    this.mostrarMensaje('Dashboard sincronizado con el mapa', 'success');
}

centrarMapaEnSeleccion() {
    if (!this.app || !this.app.regionSeleccionada) {
        this.mostrarMensaje('No hay región seleccionada en el mapa', 'warning');
        return;
    }

    const marcador = this.app.marcadoresRegiones[this.app.regionSeleccionada];
    if (marcador) {
        this.app.mapa.setView(marcador.getLatLng(), 8);
        this.mostrarMensaje('Mapa centrado en la región seleccionada', 'info');
    }
}

limpiarFiltrosDesdeDashboard() {
    if (!this.app) return;

    this.app.limpiarFiltros();
    this.mostrarMensaje('Filtros limpiados', 'info');
}

//   Cargar todos los gráficos
async cargarGraficos() {
    try {
        await this.crearGraficoPreciosTemporales('grafico-precios-temporales');
        await this.crearGraficoDistribucionRegiones('grafico-distribucion-regiones');
        await this.crearGraficoEstacionalidad('grafico-estacionalidad');

        // Configurar interactividad después de cargar los gráficos
        setTimeout(() => {
            this.configurarInteractividadGraficos();
        }, 100);
    } catch (error) {
        console.error('Error cargando gráficos:', error);
    }
}

//   Crear gráfico de precios temporales
async crearGraficoPreciosTemporales(containerId) {
    try {
        const params = new URLSearchParams();
        Object.entries(this.filtrosActuales).forEach(([key, value]) => {
            if (value && value !== '') {
                params.append(key, value);
            }
        });

        const response = await fetch(`/api/graficos/precios-temporales/?${params.toString()}`);
        const data = await response.json();

        if (data.error) {
            throw new Error(data.error);
        }

        const ctx = document.getElementById(containerId).getContext('2d');

        // Destruir gráfico anterior si existe
        if (this.graficos[containerId]) {
            this.graficos[containerId].destroy();
        }

        this.graficos[containerId] = new Chart(ctx, {
            type: 'line',
            data: data,
            options: {
                responsive: true,
                plugins: {
                    title: {
                        display: true,
                        text: 'Evolución de Precios en el Tiempo'
                    },
                    tooltip: {
                        mode: 'index',
                        intersect: false
                    }
                },
                scales: {
                    x: {
                        display: true,
                        title: {
                            display: true,
                            text: 'Fecha'
                        }
                    },
                    y: {
                        display: true,
                        title: {
                            display: true,
                            text: 'Precio ($)'
                        }
                    }
                }
            }
        });

    } catch (error) {
        console.error('Error creando gráfico de precios:', error);
        document.getElementById(containerId).parentElement.innerHTML =
            '<p class="metrica-sin-datos">No se pudieron cargar los datos del gráfico</p>';
    }
}

//   Crear gráfico de distribución por regiones
async crearGraficoDistribucionRegiones(containerId) {
    try {
        const params = new URLSearchParams();
        Object.entries(this.filtrosActuales).forEach(([key, value]) => {
            if (value && value !== '' && key !== 'region_id') { // Excluir region_id para ver todas las regiones
                params.append(key, value);
            }
        });

        const response = await fetch(`/api/graficos/distribucion-regiones/?${params.toString()}`);
        const data = await response.json();

        if (data.error) {
            throw new Error(data.error);
        }

        const ctx = document.getElementById(containerId).getContext('2d');

        if (this.graficos[containerId]) {
            this.graficos[containerId].destroy();
        }

        this.graficos[containerId] = new Chart(ctx, {
            type: 'bar',
            data: data,
            options: {
                responsive: true,
                plugins: {
                    title: {
                        display: true,
                        text: 'Distribución por Regiones'
                    }
                },
                scales: {
                    x: {
                        display: true,
                        title: {
                            display: true,
                            text: 'Regiones'
                        }
                    },
                    y: {
                        display: true,
                        title: {
                            display: true,
                            text: 'Volumen'
                        }
                    },
                    y1: {
                        display: true,
                        position: 'right',
                        title: {
                            display: true,
                            text: 'Precio Promedio ($)'
                        },
                        grid: {
                            drawOnChartArea: false
                        }
                    }
                }
            }
        });

    } catch (error) {
        console.error('Error creando gráfico de distribución:', error);
        document.getElementById(containerId).parentElement.innerHTML =
            '<p class="metrica-sin-datos">No se pudieron cargar los datos del gráfico</p>';
    }
}

//   Crear gráfico de estacionalidad
async crearGraficoEstacionalidad(containerId) {
    try {
        const params = new URLSearchParams();
        Object.entries(this.filtrosActuales).forEach(([key, value]) => {
            if (value && value !== '') {
                params.append(key, value);
            }
        });

        const response = await fetch(`/api/graficos/estacionalidad/?${params.toString()}`);
        const data = await response.json();

        if (data.error) {
            throw new Error(data.error);
        }

        const ctx = document.getElementById(containerId).getContext('2d');

        if (this.graficos[containerId]) {
            this.graficos[containerId].destroy();
        }

        this.graficos[containerId] = new Chart(ctx, {
            type: 'line',
            data: data,
            options: {
                responsive: true,
                plugins: {
                    title: {
                        display: true,
                        text: 'Estacionalidad Anual'
                    }
                },
                scales: {
                    x: {
                        display: true,
                        title: {
                            display: true,
                            text: 'Mes'
                        }
                    },
                    y: {
                        display: true,
                        title: {
                            display: true,
                            text: 'Precio Promedio ($)'
                        }
                    },
                    y1: {
                        display: true,
                        position: 'right',
                        title: {
                            display: true,
                            text: 'Volumen Promedio'
                        },
                        grid: {
                            drawOnChartArea: false
                        }
                    }
                }
            }
        });

    } catch (error) {
        console.error('Error creando gráfico de estacionalidad:', error);
        document.getElementById(containerId).parentElement.innerHTML =
            '<p class="metrica-sin-datos">No se pudieron cargar los datos del gráfico</p>';
    }
}
    mostrarMensaje(mensaje, tipo = 'info') {
        if (this.app && this.app.mostrarMensaje) {
            this.app.mostrarMensaje(mensaje, tipo);
        } else {
            // Fallback simple
            const alerta = document.createElement('div');
            alerta.style.cssText = `
                position: fixed;
                top: 20px;
                right: 20px;
                padding: 12px 20px;
                border-radius: 6px;
                color: white;
                z-index: 10000;
                font-weight: 500;
                background: ${tipo === 'info' ? '#17a2b8' : tipo === 'warning' ? '#ffc107' : '#dc3545'};
            `;
            alerta.textContent = mensaje;
            document.body.appendChild(alerta);
            setTimeout(() => alerta.remove(), 3000);
        }
    }
}

// Hacer disponible globalmente
window.dashboard = null;

// Inicializar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', function() {
    if (window.app && window.app.dashboard) {
        window.dashboard = window.app.dashboard;

    }
});