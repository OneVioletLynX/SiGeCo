// ===========================
// AUTH — helper central
// ===========================
function getToken() {
  return localStorage.getItem("sigeco_access") || "";
}

function logout() {
  localStorage.removeItem("sigeco_access");
  localStorage.removeItem("sigeco_refresh");
  localStorage.removeItem("sigeco_rol");
  localStorage.removeItem("sigeco_nombre");
  document.cookie = "sigeco_access=; path=/; max-age=0";
  window.location.href = "http://127.0.0.1:8001/";
}

async function authFetch(url, options = {}) {
  const token = getToken();
  if (!token) {
    logout();
    return;
  }

  const headers = {
    ...(options.headers || {}),
    "Authorization": `Bearer ${token}`,
  };

  const resp = await fetch(url, { ...options, headers });

  if (resp.status === 401) {
    logout();
    return;
  }

  return resp;
}

document.addEventListener("DOMContentLoaded", () => {

  if (!getToken()) {
    logout();
    return;
  }

  // ===============================
  // FILTROS
  // ===============================
  let filtroEstado   = "all";
  let filtroCarrera  = "all";
  let filtroBusqueda = "";

  // ===============================
  // FORMATEO VISUAL
  // ===============================
  function aclararColor(hex, factor = 150) {
    hex = hex.replace("#", "");
    const r = Math.min(255, parseInt(hex.substring(0, 2), 16) + factor);
    const g = Math.min(255, parseInt(hex.substring(2, 4), 16) + factor);
    const b = Math.min(255, parseInt(hex.substring(4, 6), 16) + factor);
    return `rgb(${r},${g},${b})`;
  }

  function formatearChipCarrera(nombre, color) {
    if (!nombre) return "-";
    if (!color)  return nombre;
    const fondo = aclararColor(color, 150);
    return `
      <span class="chip" style="background:${fondo}; color:${color}">
        <span class="dot" style="background:${color}"></span>
        ${nombre}
      </span>
    `;
  }

  const ESTADOS_PALETA = {
    "activo":   { bg: "#E8F5E9", text: "#2E7D32" },
    "inactivo": { bg: "#FFEBEE", text: "#C62828" },
    "baja":     { bg: "#FFF3E0", text: "#EF6C00" },
  };

  function formatearChipEstado(estado) {
    if (!estado) return "-";
    const c = ESTADOS_PALETA[estado.toLowerCase()] || { bg: "#E0E0E0", text: "#424242" };
    return `
      <span class="chip" style="background:${c.bg}; color:${c.text}">
        <span class="dot" style="background:${c.text}"></span>
        ${estado}
      </span>
    `;
  }

  // ===============================
  // TABLA + PAGINACIÓN
  // ===============================
  let alumnosData  = [];
  let paginaActual = 1;
  const POR_PAGINA = 10;

  async function cargarAlumnos() {
    let url = "http://localhost:8000/api/alumnos/?";
    if (filtroEstado  !== "all") url += `estado=${filtroEstado}&`;
    if (filtroCarrera !== "all") url += `carrera=${filtroCarrera}&`;
    if (filtroBusqueda)          url += `search=${encodeURIComponent(filtroBusqueda)}&`;

    const res = await authFetch(url);
    if (!res) return;

    const data = await res.json();

    // CORRECCIÓN: verificar que la respuesta sea un array antes de asignar
    if (!Array.isArray(data)) {
      console.error("Respuesta inesperada de la API:", data);
      return;
    }

    alumnosData  = data;
    paginaActual = 1;
    mostrarPagina();
  }

  function mostrarPagina() {
    const tbody = document.querySelector("#tablaAlumnos tbody");
    if (!tbody) return;

    tbody.innerHTML = "";

    const inicio = (paginaActual - 1) * POR_PAGINA;
    const pag    = alumnosData.slice(inicio, inicio + POR_PAGINA);

    pag.forEach(alumno => {
      const tr = document.createElement("tr");
      tr.innerHTML = `
        <td>${alumno.apellido}, ${alumno.nombre}</td>
        <td>${formatearChipCarrera(alumno.carrera_nombre, alumno.carrera_color)}</td>
        <td>${formatearChipEstado(alumno.estado_nombre)}</td>
        <td class="acciones-col">
          <div class="acciones">
            <button class="btn-baja" data-id="${alumno.id_alumno}">
              <img src="/static/shared/assets/remove.svg">
            </button>
          </div>
        </td>
      `;
      tbody.appendChild(tr);
    });

    mostrarPaginador();
  }

  function mostrarPaginador() {
    const cont = document.getElementById("paginador");
    if (!cont) return;
    cont.innerHTML = "";

    const total = Math.ceil(alumnosData.length / POR_PAGINA);
    if (total <= 1) return;

    function addBtn(label, page, disabled = false) {
      const li  = document.createElement("li");
      const btn = document.createElement("a");
      btn.href        = "#";
      btn.textContent = label;
      if (!disabled) {
        btn.addEventListener("click", e => {
          e.preventDefault();
          paginaActual = page;
          mostrarPagina();
        });
      }
      li.appendChild(btn);
      cont.appendChild(li);
    }

    addBtn("<", paginaActual - 1, paginaActual === 1);
    for (let i = 1; i <= total; i++) addBtn(i, i);
    addBtn(">", paginaActual + 1, paginaActual === total);
  }

  // ===============================
  // BAJA
  // ===============================
  async function darDeBajaAlumno(id) {
    const r = await authFetch(`http://localhost:8000/api/alumnos/${id}/`, {
      method:  "PATCH",
      headers: { "Content-Type": "application/json" },
      body:    JSON.stringify({ id_estado: 2 }),
    });
    if (r && r.ok) cargarAlumnos();
  }

  document.addEventListener("click", e => {
    const btn = e.target.closest(".btn-baja");
    if (!btn) return;
    darDeBajaAlumno(btn.dataset.id);
  });

  // ===============================
  // BOTÓN LOGOUT (si existe en el template)
  // ===============================
  const btnLogout = document.getElementById("btnLogout");
  if (btnLogout) {
    btnLogout.addEventListener("click", logout);
  }

  // ===============================
  // INICIO
  // ===============================
  if (document.getElementById("tablaAlumnos")) {
    cargarAlumnos();
  }

});