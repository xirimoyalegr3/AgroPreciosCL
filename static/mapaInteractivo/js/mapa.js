class MapaInteractivo {
    constructor() {
        this.mapa = null;
        this.regionSeleccionada = null;
        this.init();
    }

    init() {
        this.inicializarMapa();
        this.cargarResumenGeneral();
        this.cargarRegiones();
    }

    inicializarMapa() {
        // Centro de Chile
        this.mapa = L.map('mapa').setView([-35.6751, -71.5430], 5);

        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '© OpenStreetMap contributors'
        }).addTo(this.mapa);
    }

    async cargarResumenGeneral() {
        try {
            const response = await fetch('/api/resumen/');
            const data = await response.json();
            this.mostrarResumenGeneral(data);
        } catch (error) {
            console.error('Error cargando resumen:', error);
        }
    }

    mostrarResumenGeneral(data) {
        const contenedor = document.getElementById('estadisticas-globales');
        contenedor.innerHTML = `
            <div class="estadistica-item">
                <span>Total de registros:</span>
                <span class="estadistica-valor">${data.total_registros?.toLocaleString() || '0'}</span>
            </div>
            <div class="estadistica-item">
                <span>Regiones:</span>
                <span class="estadistica-valor">${data.total_regiones || '0'}</span>
            </div>
            <div class="estadistica-item">
                <span>Productos:</span>
                <span class="estadistica-valor">${data.total_productos || '0'}</span>
            </div>
        `;
    }

    cargarRegiones() {
        // Marcadores de prueba para regiones principales
        const regionesPrueba = [
            { nombre: 'Región Metropolitana', lat: -33.4489, lng: -70.6693, id: 13 },
            { nombre: 'Región de Valparaíso', lat: -33.0458, lng: -71.6197, id: 5 },
            { nombre: 'Región del Biobío', lat: -36.8269, lng: -73.0503, id: 8 },
            { nombre: 'Región de La Araucanía', lat: -38.7359, lng: -72.5907, id: 9 }
        ];

        regionesPrueba.forEach(region => {
            L.marker([region.lat, region.lng])
                .addTo(this.mapa)
                .bindPopup(`
                    <b>${region.nombre}</b><br>
                    <button onclick="app.seleccionarRegion(${region.id})">
                        Ver detalles
                    </button>
                `);
        });
    }

    async seleccionarRegion(regionId) {
        try {
            const response = await fetch(`/api/region/${regionId}/`);
            const data = await response.json();
            this.mostrarInfoRegion(data);
        } catch (error) {
            console.error('Error cargando región:', error);
        }
    }

    mostrarInfoRegion(datos) {
        const contenedor = document.getElementById('info-region');
        contenedor.innerHTML = `
            <h3>${datos.region || 'Región'}</h3>
            <p>Total productos: ${datos.total_productos || '0'}</p>
            <div id="lista-productos">
                <!-- Productos se listarán aquí -->
            </div>
        `;
    }
}

// Inicializar la aplicación
document.addEventListener('DOMContentLoaded', function() {
    window.app = new MapaInteractivo();
});