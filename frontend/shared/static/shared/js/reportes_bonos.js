document.addEventListener("DOMContentLoaded", () => {
    if (!getToken()) { logout(); return; }

    const API = "http://127.0.0.1:8000";

    const filtroCarrera    = document.getElementById("filtroCarrera");
    const filtroAnio       = document.getElementById("filtroAnio");
    const chkIngresantes   = document.getElementById("chkIngresantes");
    const btnCargar        = document.getElementById("btnCargar");
    const matrizArea       = document.getElementById("matrizArea");
    const matrizMensaje    = document.getElementById("matrizMensaje");
    const matrizMensajeTexto = document.getElementById("matrizMensajeTexto");
    const matrizMensajeIcon  = document.getElementById("matrizMensajeIcon");
    const matrizHead       = document.getElementById("matrizHead");
    const matrizBody       = document.getElementById("matrizBody");

    // ── Año: desde 2020 hasta año actual + 1 ──
    const anioActual = new Date().getFullYear();
    for (let y = anioActual + 1; y >= 2020; y--) {
        const opt = document.createElement("option");
        opt.value = y;
        opt.textContent = y;
        if (y === anioActual) opt.selected = true;
        filtroAnio.appendChild(opt);
    }

    // ── Carreras ──
    async function cargarCarreras() {
        const resp = await authFetch(`${API}/api/carreras/`);
        if (!resp || !resp.ok) return;
        const carreras = await resp.json();
        carreras.forEach(c => {
            const opt = document.createElement("option");
            opt.value = c.id_carrera;
            opt.textContent = c.descripcion;
            filtroCarrera.appendChild(opt);
        });
    }

    filtroCarrera.addEventListener("change", () => {
        btnCargar.disabled = !filtroCarrera.value;
    });

    // ── Mostrar mensaje ──
    function setMensaje(texto, icono = "receipt_long") {
        matrizArea.style.display = "none";
        matrizMensaje.style.display = "block";
        matrizMensajeTexto.textContent = texto;
        matrizMensajeIcon.textContent  = icono;
    }

    // ── Cargar y renderizar matriz ──
    async function cargarMatriz() {
        const carreraId    = filtroCarrera.value;
        const anio         = filtroAnio.value;
        const ingresantes  = chkIngresantes.checked;

        if (!carreraId) { setMensaje("Seleccioná una carrera para ver los datos."); return; }

        setMensaje("Cargando...", "hourglass_empty");

        const url = new URL(`${API}/api/bonos_matriz/`);
        url.searchParams.set("carrera",     carreraId);
        url.searchParams.set("anio",        anio);
        url.searchParams.set("ingresantes", ingresantes);

        const resp = await authFetch(url.toString());
        if (!resp || !resp.ok) {
            showAlert("No se pudieron cargar los datos.", "error");
            setMensaje("Error al cargar los datos.", "error_outline");
            return;
        }

        const data = await resp.json();

        if (!data.alumnos || !data.alumnos.length) {
            setMensaje("Sin alumnos para los filtros seleccionados.", "people");
            return;
        }

        renderMatriz(data, anio);
    }

    function renderMatriz(data, anio) {
        const { meses, alumnos } = data;
        // Abreviar nombres de mes (primeras 3 letras)
        const mesAbrev = meses.map(m => m.slice(0, 3));

        // ── Header ──
        matrizHead.innerHTML = "";
        const trH = document.createElement("tr");
        trH.innerHTML = `
            <th style="text-align:left; min-width:70px;">Legajo</th>
            <th style="text-align:left; min-width:200px;">Alumno</th>
            ${mesAbrev.map(m => `<th class="col-mes">${m}</th>`).join("")}
            <th class="col-mes" style="min-width:52px; color:var(--color-primary);">Total</th>
        `;
        matrizHead.appendChild(trH);

        // ── Body ──
        matrizBody.innerHTML = "";
        alumnos.forEach(a => {
            const tr = document.createElement("tr");
            if (a.es_ingresante) tr.classList.add("fila-ingresante");

            const celdaMeses = a.pagos
                .map(p => p
                    ? `<td class="col-mes"><span class="pago-si">✓</span></td>`
                    : `<td class="col-mes"><span class="pago-no">−</span></td>`)
                .join("");

            const badgeIng = a.es_ingresante
                ? `<span class="badge-ingresante">ingresante</span>`
                : "";

            tr.innerHTML = `
                <td class="col-legajo">${a.legajo}</td>
                <td class="col-nombre">${a.nombre}${badgeIng}</td>
                ${celdaMeses}
                <td class="col-total">${a.total_pagados}/${meses.length}</td>
            `;
            matrizBody.appendChild(tr);
        });

        matrizMensaje.style.display = "none";
        matrizArea.style.display    = "block";
    }

    btnCargar.addEventListener("click", cargarMatriz);

    // ── Recargar al cambiar año o checkbox sin resetear filtros ──
    filtroAnio.addEventListener("change", () => {
        if (filtroCarrera.value) cargarMatriz();
    });
    chkIngresantes.addEventListener("change", () => {
        if (filtroCarrera.value) cargarMatriz();
    });

    // ── Inicio ──
    setMensaje("Seleccioná una carrera y un año para ver los datos.");
    cargarCarreras();
});
