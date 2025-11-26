document.addEventListener("DOMContentLoaded", () => {
    const tabla = document.querySelector("#tabla-alumnos tbody");
    const downloadButton = document.getElementById('generar-pdf-btn');
    const filtroCarreraSelect = document.getElementById("filtroCarrera");
    const filtroEstadoSelect = document.getElementById("filtroEstado");

    let mapaEstados = {};
    let mapaCarreras = {};
    let filtroCarrera = "all";
    let filtroEstado = "all";

    // ----------------------------------------------------------
    // 🔹 Cargar carreras
    // ----------------------------------------------------------
    async function cargarCarreras() {
        const response = await fetch("http://localhost:8000/api/carreras/");
        const carreras = await response.json();

        carreras.forEach(c => {
            const id = String(c.id_carrera);
            mapaCarreras[id] = c.descripcion;

            const opt = document.createElement("option");
            opt.value = id;
            opt.textContent = c.descripcion;
            filtroCarreraSelect.appendChild(opt);
        });
    }

    // ----------------------------------------------------------
    // 🔹 Cargar estados (SELECT ÚNICO)
    // ----------------------------------------------------------
    async function cargarEstados() {
        const response = await fetch("http://localhost:8000/api/estados/");
        const estados = await response.json();

        estados.forEach(e => {
            const id = String(e.id_estado);
            mapaEstados[id] = e.descripcion;

            const opt = document.createElement("option");
            opt.value = id;
            opt.textContent = e.descripcion;
            filtroEstadoSelect.appendChild(opt);
        });
    }

    // ----------------------------------------------------------
    // 🔹 Cargar alumnos (con filtros actualizados)
    // ----------------------------------------------------------
    async function cargarAlumnos() {
        let url = new URL("http://localhost:8000/api/alumnos/");

        if (filtroEstado !== "all") {
            url.searchParams.append('estado', filtroEstado); 
        }

        if (filtroCarrera !== "all") {
            url.searchParams.append('carrera', filtroCarrera); 
        }

        const response = await fetch(url.toString());
        const alumnos = await response.json();

        tabla.innerHTML = "";

        alumnos.forEach(alumno => {
            const tr = document.createElement("tr");
            const estadoDesc = mapaEstados[String(alumno.estado_actual)] ?? "-";
            const carreraDesc = mapaCarreras[String(alumno.carrera_actual)] ?? "-";

            tr.innerHTML = `
                <td>${alumno.legajo ?? '-'}</td>
                <td>${alumno.apellido ?? '-'}, ${alumno.nombre ?? '-'}</td>
                <td>${alumno.dni ?? '-'}</td>
                <td>${estadoDesc}</td>
                <td>${carreraDesc}</td>
            `;
            tabla.appendChild(tr);
        });
    }

    // ----------------------------------------------------------
    // 🔹 Eventos
    // ----------------------------------------------------------
    filtroEstadoSelect.addEventListener("change", async e => {
        filtroEstado = e.target.value;
        await cargarAlumnos();
    });

    filtroCarreraSelect.addEventListener("change", async e => {
        filtroCarrera = e.target.value;
        await cargarAlumnos();
    });

    // ----------------------------------------------------------
    // 🔹 Generación de PDF
    // ----------------------------------------------------------
    if (downloadButton) {
        // Descarga
        downloadButton.addEventListener('click', function () {
            let pdfUrl = new URL('http://127.0.0.1:8000/api/generar_pdf_alumnos');

            // Filtros en la URL
            if (filtroEstado !== "all") {
                pdfUrl.searchParams.append('estado', filtroEstado); 
            }

            if (filtroCarrera !== "all") {
                pdfUrl.searchParams.append('carrera', filtroCarrera);
            }
            window.open(pdfUrl.toString(), '_self'); 
        });
    }

    // ----------------------------------------------------------
    // 🔹 Inicialización
    // ----------------------------------------------------------
    (async () => {
        await Promise.all([cargarCarreras(), cargarEstados()]);
        await cargarAlumnos();
    })();
});