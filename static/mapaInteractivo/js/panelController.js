class PanelController {
    constructor() {
        this.panelEstado = 'normal'; // normal, contraido, expandido
        this.seccionActiva = 'resumen'; // resumen, filtros, info, analisis
        this.init();
    }

    init() {
        this.crearControles();
        this.configurarEventListeners();

    }

    crearControles() {
        const panelLateral = document.getElementById('panel-lateral');

        // Crear controles de expansión
        const panelControls = document.createElement('div');
        panelControls.className = 'panel-controls';
        panelControls.innerHTML = `
            <button class="btn-expand-panel" id="btn-contraer-panel" title="Contraer panel">
                ◀
            </button>
        `;

        // Crear iconos para estado contraído
        const panelIconos = document.createElement('div');
        panelIconos.className = 'panel-iconos';
        panelIconos.innerHTML = `
            <div class="icono-panel active" data-seccion="resumen" title="Resumen General">

            </div>
            <div class="icono-panel" data-seccion="filtros" title="Filtros">

            </div>
            <div class="icono-panel" data-seccion="info" title="Información Región">

            </div>
            <div class="icono-panel" data-seccion="analisis" title="Análisis">

            </div>
            <div class="icono-panel" data-seccion="expandir" title="Expandir Panel">
                ▶
            </div>
        `;

        panelLateral.appendChild(panelControls);
        panelLateral.appendChild(panelIconos);
    }

    configurarEventListeners() {
        // Botón contraer/expandir
        document.getElementById('btn-contraer-panel').addEventListener('click', () => {
            this.contraerPanel();
        });

        // Iconos del panel contraído
        document.querySelectorAll('.icono-panel').forEach(icono => {
            icono.addEventListener('click', (e) => {
                const seccion = e.target.getAttribute('data-seccion');
                if (seccion === 'expandir') {
                    this.expandirPanel();
                } else {
                    this.mostrarSeccion(seccion);
                }
            });
        });

        // Evento para cambiar botón cuando el panel está contraído
        document.addEventListener('click', (e) => {
            if (this.panelEstado === 'contraido' && !e.target.closest('#panel-lateral')) {
                this.mostrarSeccion('resumen');
            }
        });
    }

    contraerPanel() {
        this.panelEstado = 'contraido';
        const panel = document.getElementById('panel-lateral');
        const boton = document.getElementById('btn-contraer-panel');

        panel.classList.add('panel-contraido');
        panel.classList.remove('panel-expandido');
        boton.innerHTML = '▶';
        boton.title = 'Expandir panel';

    }

    expandirPanel() {
        this.panelEstado = 'normal';
        const panel = document.getElementById('panel-lateral');
        const boton = document.getElementById('btn-contraer-panel');

        panel.classList.remove('panel-contraido');
        panel.classList.remove('panel-expandido');
        boton.innerHTML = '◀';
        boton.title = 'Contraer panel';

    }

    expandirMaximo() {
        this.panelEstado = 'expandido';
        const panel = document.getElementById('panel-lateral');
        const boton = document.getElementById('btn-contraer-panel');

        panel.classList.remove('panel-contraido');
        panel.classList.add('panel-expandido');
        boton.innerHTML = '◀';
        boton.title = 'Contraer panel';

    }

    mostrarSeccion(seccion) {
        this.seccionActiva = seccion;

        // Ocultar todas las secciones
        document.querySelectorAll('#panel-lateral > div:not(.panel-controls):not(.panel-iconos)').forEach(div => {
            div.style.display = 'none';
            div.style.opacity = '0';
            div.style.height = '0';
            div.style.padding = '0';
            div.style.margin = '0';
            div.style.overflow = 'hidden';
        });

        // Mostrar solo la sección activa
        let seccionActivaElement = null;

        switch(seccion) {
            case 'resumen':
                seccionActivaElement = document.getElementById('resumen-general');
                break;
            case 'filtros':
                seccionActivaElement = document.getElementById('filtros-container');
                break;
            case 'info':
                seccionActivaElement = document.getElementById('info-region');
                break;
            case 'analisis':
                seccionActivaElement = document.querySelector('.panel-analisis') || document.getElementById('panel-analisis');
                break;
        }

        if (seccionActivaElement) {
            seccionActivaElement.style.display = 'block';
            seccionActivaElement.style.opacity = '1';
            seccionActivaElement.style.height = 'auto';
            seccionActivaElement.style.padding = '20px';
            seccionActivaElement.style.margin = '10px 0';
            seccionActivaElement.style.overflow = 'visible';
        }

        // Actualizar iconos activos
        document.querySelectorAll('.icono-panel').forEach(icono => {
            icono.classList.remove('active');
        });

        const iconoActivo = document.querySelector(`.icono-panel[data-seccion="${seccion}"]`);
        if (iconoActivo) {
            iconoActivo.classList.add('active');
        }

    }

    // Método para ajustar texto según tamaño del panel
    ajustarTipografia() {
        const panel = document.getElementById('panel-lateral');
        const esExpandido = panel.classList.contains('panel-expandido');

        if (esExpandido) {
            document.documentElement.style.setProperty('--panel-font-size', '15px');
            document.documentElement.style.setProperty('--panel-line-height', '1.6');
        } else {
            document.documentElement.style.setProperty('--panel-font-size', '14px');
            document.documentElement.style.setProperty('--panel-line-height', '1.5');
        }
    }
}