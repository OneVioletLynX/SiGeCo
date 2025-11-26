// shared/js/reportes_bonos.js

document.addEventListener("DOMContentLoaded", () => {
    const downloadButton = document.getElementById('generar-pdf-bonos-btn');
    const fechaDesdeInput = document.getElementById('fecha_desde');
    const fechaHastaInput = document.getElementById('fecha_hasta');

    // ----------------------------------------------------------
    // 🔹 Generación de PDF de Bonos
    // ----------------------------------------------------------
    if (downloadButton) {
        downloadButton.addEventListener('click', function () {
            const fechaDesde = fechaDesdeInput.value;
            const fechaHasta = fechaHastaInput.value;
            
            if (!fechaDesde || !fechaHasta) {
                alert('Por favor, selecciona las fechas "Desde" y "Hasta".');
                return;
            }

            // URL del backend para generar el PDF de bonos
            let pdfUrl = new URL('http://127.0.0.1:8000/api/generar_pdf_bonos/'); // Ajusta esta URL a tu configuración real

            // Filtros en la URL
            pdfUrl.searchParams.append('fecha_desde', fechaDesde); 
            pdfUrl.searchParams.append('fecha_hasta', fechaHasta);
            
            window.open(pdfUrl.toString(), '_self'); 
        });
    }
    
    // Opcional: Agregar lógica para cargar y mostrar una tabla de previsualización aquí
    
});