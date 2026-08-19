document.addEventListener("DOMContentLoaded", () => {
  if (!getToken()) { logout(); return; }

  const API = "http://127.0.0.1:8000";

  const selCarrera     = document.getElementById("filtroCarrera");
  const selAnio        = document.getElementById("filtroAnio");
  const btnCargar      = document.getElementById("btn-cargar");
  const btnPdf         = document.getElementById("btn-pdf");
  const msgCargando    = document.getElementById("msg-cargando");

  const secGeneral     = document.getElementById("seccion-general");
  const secCarrera     = document.getElementById("seccion-carrera");
  const secIngresantes = document.getElementById("seccion-ingresantes");

  // ===========================
  // CARGA DE FILTROS
  // ===========================
  async function cargarFiltros() {
    const res = await authFetch(`${API}/api/carreras/`);
    if (!res || !res.ok) return;
    const carreras = await res.json();
    carreras.forEach(c => {
      const opt = document.createElement("option");
      opt.value       = c.id_carrera;
      opt.textContent = c.descripcion;
      selCarrera.appendChild(opt);
    });

    const anioActual = new Date().getFullYear();
    for (let y = anioActual; y >= anioActual - 10; y--) {
      const opt = document.createElement("option");
      opt.value       = y;
      opt.textContent = y;
      selAnio.appendChild(opt);
    }
  }

  // ===========================
  // RENDERIZADO DE TABLAS
  // ===========================
  function renderTablaLocalidad(tbodyId, filas, colLabel = "Alumnos", showPct = false, total = 0) {
    const tbody = document.querySelector(`#${tbodyId} tbody`);
    if (!tbody) return;
    tbody.innerHTML = "";

    if (!filas || !filas.length) {
      tbody.innerHTML = `<tr><td colspan="5" style="text-align:center; color:var(--text-muted); padding:1.5rem;">Sin datos para mostrar.</td></tr>`;
      return;
    }

    filas.forEach((row, i) => {
      const pct = total > 0 ? ((row.cantidad / total) * 100).toFixed(1) : "—";
      const tr = document.createElement("tr");
      tr.innerHTML = `
        <td>${i + 1}</td>
        <td>${row.localidad}</td>
        <td>${row.provincia}</td>
        <td style="text-align:right; font-weight:600;">${row.cantidad}</td>
        ${showPct ? `<td style="text-align:right; color:var(--text-muted);">${pct}%</td>` : ""}
      `;
      tbody.appendChild(tr);
    });
  }

  // ===========================
  // CARGA DE DATOS
  // ===========================
  async function cargarDatos() {
    const carreraId = selCarrera.value || "";
    const anio      = selAnio.value   || "";

    let url = `${API}/api/preview_demografico/?`;
    if (carreraId) url += `carrera=${carreraId}&`;
    if (anio)      url += `anio=${anio}&`;

    msgCargando.style.display    = "block";
    secGeneral.style.display     = "none";
    secCarrera.style.display     = "none";
    secIngresantes.style.display = "none";

    const res = await authFetch(url);
    msgCargando.style.display = "none";

    if (!res || !res.ok) return;
    const data = await res.json();

    // Sección 1 — general
    document.getElementById("badge-total").textContent = `Total: ${data.total_general} alumnos`;
    renderTablaLocalidad("tabla-general", data.general, "Alumnos", true, data.total_general);
    secGeneral.style.display = "block";

    // Sección 2 — por carrera
    if (data.carrera_nombre && data.por_carrera && data.por_carrera.length) {
      document.getElementById("titulo-carrera").textContent =
        `Distribución por localidad — ${data.carrera_nombre}`;
      renderTablaLocalidad("tabla-carrera", data.por_carrera, "Alumnos", false);
      secCarrera.style.display = "block";
    }

    // Sección 3 — ingresantes
    const labelIng = anio ? `Ingresantes ${anio} por localidad` : "Ingresantes por localidad";
    document.getElementById("titulo-ingresantes").textContent = labelIng;
    renderTablaLocalidad("tabla-ingresantes", data.ingresantes, "Ingresantes", false);
    document.getElementById("titulo-ingresantes").innerHTML =
      `${labelIng} <span style="font-size:0.75rem; background:#dcfce7; color:#16a34a;
        padding:2px 10px; border-radius:20px; font-weight:600; text-transform:none; letter-spacing:0; margin-left:0.4rem;">
        Total: ${data.total_ingresantes}
       </span>`;
    secIngresantes.style.display = "block";
  }

  // ===========================
  // GENERAR PDF
  // ===========================
  btnPdf.addEventListener("click", () => {
    const carreraId = selCarrera.value || "";
    const anio      = selAnio.value   || "";
    let url = `${API}/api/generar_pdf_demografico/?`;
    if (carreraId) url += `carrera=${carreraId}&`;
    if (anio)      url += `anio=${anio}&`;
    window.open(url, "_self");
  });

  // ===========================
  // EVENTOS
  // ===========================
  btnCargar.addEventListener("click", cargarDatos);

  // ===========================
  // INICIO
  // ===========================
  cargarFiltros().then(() => cargarDatos());
});
