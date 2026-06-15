document.addEventListener("DOMContentLoaded", () => {
    if (!getToken()) { logout(); return; }

    const API = "http://127.0.0.1:8000";
    const tabla = document.querySelector("#tabla-alumnos tbody");
    const downloadButton = document.getElementById('generar-pdf-btn');
    const filtroCarreraSelect = document.getElementById("filtroCarrera");
    const filtroEstadoSelect = document.getElementById("filtroEstado");

    let mapaEstados = {};
    let mapaCarreras = {};
    let filtroCarrera = "all";
    let filtroEstado = "all";

    function setLoading() {
        if (tabla) tabla.innerHTML = `<tr><td colspan="5" style="text-align:center;padding:2rem;color:var(--text-muted);">Cargando...</td></tr>`;
    }

    function setEmpty() {
        if (tabla) tabla.innerHTML = `
            <tr>
                <td colspan="5" style="text-align:center;padding:3rem;color:var(--text-muted);">
                    <span class="material-icons" style="font-size:2.5rem;display:block;margin-bottom:0.5rem;opacity:0.4;">people</span>
                    Sin alumnos para los filtros seleccionados.
                </td>
            </tr>`;
    }

    async function cargarCarreras() {
        const resp = await authFetch(`${API}/api/carreras/`);
        if (!resp || !resp.ok) return;
        const carreras = await resp.json();
        carreras.forEach(c => {
            mapaCarreras[String(c.id_carrera)] = c.descripcion;
            const opt = document.createElement("option");
            opt.value = String(c.id_carrera);
            opt.textContent = c.descripcion;
            filtroCarreraSelect.appendChild(opt);
        });
    }

    async function cargarEstados() {
        const resp = await authFetch(`${API}/api/estados/`);
        if (!resp || !resp.ok) return;
        const estados = await resp.json();
        estados.forEach(e => {
            mapaEstados[String(e.id_estado)] = e.descripcion;
            const opt = document.createElement("option");
            opt.value = String(e.id_estado);
            opt.textContent = e.descripcion;
            filtroEstadoSelect.appendChild(opt);
        });
    }

    async function cargarAlumnos() {
        setLoading();
        const url = new URL(`${API}/api/alumnos/`);
        if (filtroEstado !== "all") url.searchParams.append('estado', filtroEstado);
        if (filtroCarrera !== "all") url.searchParams.append('carrera', filtroCarrera);

        const resp = await authFetch(url.toString());
        if (!resp || !resp.ok) {
            showAlert("No se pudieron cargar los alumnos.", "error");
            setEmpty();
            return;
        }
        const alumnos = await resp.json();

        if (!tabla) return;
        tabla.innerHTML = "";

        if (!alumnos.length) { setEmpty(); return; }

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

    filtroEstadoSelect?.addEventListener("change", e => {
        filtroEstado = e.target.value;
        cargarAlumnos();
    });

    filtroCarreraSelect?.addEventListener("change", e => {
        filtroCarrera = e.target.value;
        cargarAlumnos();
    });

    downloadButton?.addEventListener('click', () => {
        const pdfUrl = new URL(`${API}/api/generar_pdf_alumnos/`);
        if (filtroEstado !== "all") pdfUrl.searchParams.append('estado', filtroEstado);
        if (filtroCarrera !== "all") pdfUrl.searchParams.append('carrera', filtroCarrera);
        window.open(pdfUrl.toString(), '_self');
    });

    (async () => {
        await Promise.all([cargarCarreras(), cargarEstados()]);
        await cargarAlumnos();
    })();
});
