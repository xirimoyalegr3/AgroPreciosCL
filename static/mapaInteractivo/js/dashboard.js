// static/mapaInteractivo/js/dashboard.js
class DashboardAnalisis {
    constructor(app) {
        this.app = app;
        this.datos = null;
        this.estado = 'cerrado';
        this.init();
    }

    init() {
        this.crearEstructuraHTML();
        this.configurarEventListeners();

    }

    crearEstructuraHTML() {
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
                <h2> Dashboard de Análisis de Negocios</h2>
                <div class="dashboard-controls">
                    <button class="btn-dashboard-control" id="minimizar-dashboard">

                    </button>
                    <button class="btn-dashboard-control" id="cerrar-dashboard">

                    </button>
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
    }

    configurarEventListeners() {
        // Botón abrir dashboard
        document.getElementById('abrir-dashboard').addEventListener('click', () => {
            this.abrir();
        });

        // Controles del dashboard
        document.getElementById('minimizar-dashboard').addEventListener('click', () => {
            this.minimizar();
        });

        document.getElementById('cerrar-dashboard').addEventListener('click', () => {
            this.cerrar();
        });

        // Cerrar con overlay
        document.getElementById('dashboard-overlay').addEventListener('click', (e) => {
            if (e.target.id === 'dashboard-overlay') {
                this.cerrar();
            }
        });
    }

    async abrir() {
        this.estado = 'abierto';
        document.getElementById('dashboard-overlay').style.display = 'block';
        document.getElementById('dashboard-container').style.display = 'block';

        document.getElementById('dashboard-container').classList.remove('dashboard-minimized');

        await this.cargarDatosDashboard();
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

    async cargarDatosDashboard() {
        try {

            const response = await fetch('/api/dashboard-analisis/', {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                },
                timeout: 10000 // 10 segundos timeout
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            this.datos = await response.json();

            this.mostrarDashboard();

        } catch (error) {

            // Usar datos de ejemplo como fallback
            this.datos = this.generarDatosEjemplo();
            this.mostrarDashboard();
            this.mostrarMensaje(' Usando datos de ejemplo - La API no está disponible temporalmente', 'warning');
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

    mostrarDashboard() {
        const content = document.getElementById('dashboard-content');

        content.innerHTML = `
            <!-- SECCIÓN 1: MÉTRICAS PRINCIPALES -->
            <div class="dashboard-section">
                <h3> Métricas Clave de Negocio</h3>
                <div class="metricas-grid">
                    ${this.generarMetricasPrincipales()}
                </div>
            </div>

            <!-- SECCIÓN 2: ANÁLISIS DE PRECIOS -->
            <div class="dashboard-section">
                <h3> Análisis de Precios por Región</h3>
                ${this.generarAnalisisPrecios()}
            </div>

            <!-- SECCIÓN 3: ANÁLISIS DE VOLÚMENES -->
            <div class="dashboard-section">
                <h3> Análisis de Volúmenes Comerciales</h3>
                ${this.generarAnalisisVolumenes()}
            </div>

            <!-- SECCIÓN 4: OPORTUNIDADES DE MERCADO -->
            <div class="dashboard-section">
                <h3> Oportunidades de Negocio</h3>
                ${this.generarOportunidadesMercado()}
            </div>

            <!-- SECCIÓN 5: TENDENCIAS TEMPORALES -->
            <div class="dashboard-section">
                <h3> Análisis Temporal</h3>
                ${this.generarAnalisisTemporal()}
            </div>

            <!-- BOTONES DE EXPORTACIÓN -->
            <div class="botones-exportacion">
               <button class="btn-exportar btn-exportar-pdf" onclick="window.dashboard.exportarPDF()">
        Exportar a PDF
    </button>
    <button class="btn-exportar btn-exportar-excel" onclick="window.dashboard.exportarExcel()">
        Exportar a Excel
    </button>
            </div>
        `;
        // En mostrarDashboard(), después de crear el HTML:
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

    generarMetricasPrincipales() {
        if (!this.datos || !this.datos.metricas_principales) {
            return '<p class="metrica-sin-datos">No hay datos disponibles</p>';
        }

        const metricas = this.datos.metricas_principales;

        const crearMetricaCard = (valor, label, esPorcentaje = false) => {
            const mostrarValor = valor === 'N/A' || valor === 0 || valor === null;
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
        
        // Usar window para acceder a la función globalmente
        const link = document.createElement('a');
        link.href = '/api/exportar-pdf/';
        link.download = 'reporte_analisis_agroprecios.pdf';
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
        
        const link = document.createElement('a');
        link.href = '/api/exportar-excel/';
        link.download = 'reporte_analisis_agroprecios.xlsx';
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