class PanelSimple {
    constructor() {
        this.isDragging = false;
        this.startX = 0;
        this.startWidth = 0;
        this.handle = null;
        this.init();
    }

    init() {
        this.handle = document.querySelector('.panel-drag-handle');
        this.configurarEventListeners();
        this.actualizarPosicionHandle();

    }

    configurarEventListeners() {
        const panel = document.getElementById('panel-lateral');

        // Evento para el handle
        this.handle.addEventListener('mousedown', (e) => {
            this.iniciarArrastre(e, panel);
        });

        // Evento para el borde derecho del panel
        panel.addEventListener('mousedown', (e) => {
            if (e.offsetX > panel.offsetWidth - 20) {
                this.iniciarArrastre(e, panel);
            }
        });

        // Actualizar posición del handle cuando cambie el tamaño
        new ResizeObserver(() => {
            this.actualizarPosicionHandle();
        }).observe(panel);
    }

    actualizarPosicionHandle() {
        const panel = document.getElementById('panel-lateral');
        const panelRect = panel.getBoundingClientRect();
        this.handle.style.left = (panelRect.right - 8) + 'px';
    }

    iniciarArrastre(e, panel) {
        this.isDragging = true;
        this.startX = e.clientX;
        this.startWidth = panel.offsetWidth;

        document.addEventListener('mousemove', this.mouseMoveHandler.bind(this));
        document.addEventListener('mouseup', this.mouseUpHandler.bind(this));
        e.preventDefault();

        document.body.style.cursor = 'col-resize';
        document.body.style.userSelect = 'none';
    }

    mouseMoveHandler(e) {
        if (!this.isDragging) return;

        const delta = this.startX - e.clientX;
        const newWidth = this.startWidth + delta;

        if (newWidth >= 300 && newWidth <= 800) {
            const panel = document.getElementById('panel-lateral');
            panel.style.width = newWidth + 'px';
            this.actualizarPosicionHandle();
            this.ajustarTipografia(newWidth);
        }
    }

    mouseUpHandler() {
        this.isDragging = false;
        document.removeEventListener('mousemove', this.mouseMoveHandler.bind(this));
        document.removeEventListener('mouseup', this.mouseUpHandler.bind(this));

        document.body.style.cursor = '';
        document.body.style.userSelect = '';
    }

    ajustarTipografia(ancho) {
        const panel = document.getElementById('panel-lateral');

        if (ancho >= 600) {
            panel.style.fontSize = '16px';
            panel.style.lineHeight = '1.6';
        } else if (ancho >= 500) {
            panel.style.fontSize = '15px';
            panel.style.lineHeight = '1.55';
        } else {
            panel.style.fontSize = '14px';
            panel.style.lineHeight = '1.5';
        }
    }
}