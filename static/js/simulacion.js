document.addEventListener("DOMContentLoaded", () => {
    console.log("Simulador cargado correctamente.");

    const btn = document.getElementById("btn-calcular");
    const cantidadInput = document.getElementById("cantidad");
    const productoSelect = document.getElementById("producto");
    const resultadoTexto = document.getElementById("resultado-texto");

    btn.addEventListener("click", () => {
        const cantidad = parseFloat(cantidadInput.value) || 0;
        const producto = productoSelect.value;

        if (cantidad <= 0) {
            resultadoTexto.textContent = "Por favor, ingrese una cantidad válida.";
            return;
        }

        // Simulación simple — puede reemplazarse por una lógica real
        const precioUnitario = Math.random() * (2500 - 800) + 800;
        const total = (cantidad * precioUnitario).toFixed(0);

        resultadoTexto.innerHTML = `
            <strong>Producto:</strong> ${producto}<br>
            <strong>Cantidad:</strong> ${cantidad}<br>
            <strong>Precio estimado unitario:</strong> $${precioUnitario.toFixed(0)}<br>
            <strong>Total estimado:</strong> $${total}
        `;
    });
});
