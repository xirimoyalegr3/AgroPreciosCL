// --- Draggable de las cajas solo con el handle ---
function makeDraggable(card) {
    const handle = card.querySelector('.drag-handle');
    let offsetX, offsetY, isDragging = false;

    handle.addEventListener('mousedown', (e) => {
        isDragging = true;
        offsetX = e.clientX - card.offsetLeft;
        offsetY = e.clientY - card.offsetTop;
        card.style.zIndex = 999;
        e.preventDefault(); // Evita que otros elementos capturen el evento
    });

    document.addEventListener('mousemove', (e) => {
        if (!isDragging) return;
        card.style.left = (e.pageX - offsetX) + 'px';
        card.style.top = (e.pageY - offsetY) + 'px';
    });

    document.addEventListener('mouseup', () => {
        if (isDragging) isDragging = false;
        card.style.zIndex = 1;
    });

    card.ondragstart = () => false;
}

// Aplica solo a las cajas flotantes
document.querySelectorAll('.floating-box').forEach(makeDraggable);

// --- Gráfico demo (Chart.js) ---
const chartCanvas = document.getElementById('chart');
if(chartCanvas) {
    const ctx = chartCanvas.getContext('2d');
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: ["Enero", "Febrero", "Marzo", "Abril", "Mayo"],
            datasets: [{
                label: 'Precio Promedio Tomate',
                data: [800, 900, 1000, 950, 1100],
                borderColor: 'red',
                backgroundColor: 'rgba(255,0,0,0.2)',
                fill: true
            }]
        },
        options: {
            maintainAspectRatio: false,
            responsive: true
        }
    });
}

document.addEventListener('DOMContentLoaded', function() {
    // Inicializa el mapa centrado en Chile
    const map = L.map('map').setView([-33.45, -70.66], 6);

    // Capa base de OpenStreetMap
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; OpenStreetMap contributors'
    }).addTo(map);

    // Marcador principal en Santiago
    const marker = L.marker([-33.45, -70.66]).addTo(map);
    marker.bindPopup('<b>Santiago</b><br>Precio promedio: $1.200').openPopup();

    // Otros ejemplos de regiones
    const regiones = [
        { nombre: "Valparaíso", coords: [-33.0472, -71.6127], precio: 1100 },
        { nombre: "Concepción", coords: [-36.8269, -73.0498], precio: 950 },
        { nombre: "La Serena", coords: [-29.9045, -71.2489], precio: 1050 },
    ];

    regiones.forEach(r => {
        L.marker(r.coords)
            .addTo(map)
            .bindPopup(`<b>${r.nombre}</b><br>Precio promedio: $${r.precio}`);
    });
});
