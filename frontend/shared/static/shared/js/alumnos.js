// Auth global desde auth.js (cargado en base.html)

document.addEventListener("DOMContentLoaded", () => {

  if (!getToken()) { logout(); return; }

  const API = "http://127.0.0.1:8000/api";

  let filtroEstado   = "1";  // por defecto solo activos
  let filtroCarrera  = "all";
  let filtroBusqueda = "";
  let searchTimeout  = null;

  // ===============================
  // AVATAR CON INICIALES
  // ===============================
  const AVATAR_COLORS = [
    ["#e0f2fe","#0369a1"], ["#dcfce7","#16a34a"], ["#ede9fe","#7c3aed"],
    ["#fef3c7","#d97706"], ["#fce7f3","#db2777"], ["#fee2e2","#dc2626"],
    ["#f0fdf4","#15803d"], ["#eff6ff","#1d4ed8"],
  ];

  function avatarColor(texto) {
    let h = 0;
    for (let i = 0; i < texto.length; i++) h = texto.charCodeAt(i) + ((h << 5) - h);
    return AVATAR_COLORS[Math.abs(h) % AVATAR_COLORS.length];
  }

  function renderAvatar(nombre, apellido) {
    const ini  = ((apellido?.[0] ?? "") + (nombre?.[0] ?? "")).toUpperCase();
    const [bg, color] = avatarColor((apellido + nombre).toLowerCase());
    return `<div style="width:36px; height:36px; border-radius:50%; background:${bg};
      color:${color}; font-size:0.78rem; font-weight:800;
      display:flex; align-items:center; justify-content:center;
      flex-shrink:0; letter-spacing:0.03em;">${ini}</div>`;
  }

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

  function formatearChipCarreras(carreras) {
    if (!carreras || carreras.length === 0) return "-";
    return carreras.map(c => {
      if (!c.color) return c.descripcion;
      const fondo = aclararColor(c.color, 150);
      return `<span class="chip" style="background:${fondo}; color:${c.color}">
        <span class="dot" style="background:${c.color}"></span>${c.descripcion}
      </span>`;
    }).join(" ");
  }

  const ESTADOS_PALETA = {
    "activo":   { bg: "#E8F5E9", text: "#2E7D32" },
    "inactivo": { bg: "#FFEBEE", text: "#C62828" },
    "baja":     { bg: "#FFF3E0", text: "#EF6C00" },
  };

  function formatearChipEstado(estado) {
    if (!estado) return "-";
    const c = ESTADOS_PALETA[estado.toLowerCase()] || { bg: "#E0E0E0", text: "#424242" };
    return `<span class="chip" style="background:${c.bg}; color:${c.text}">
      <span class="dot" style="background:${c.text}"></span>${estado}
    </span>`;
  }

  // ===============================
  // TABLA + PAGINACIÓN
  // ===============================
  let alumnosData  = [];
  let paginaActual = 1;
  const POR_PAGINA = 10;

  async function cargarAlumnos() {
    const tbody = document.querySelector("#tablaAlumnos tbody");
    if (tbody) tbody.innerHTML = `<tr><td colspan="4" style="text-align:center;padding:2rem;color:var(--text-muted);">Cargando...</td></tr>`;

    let url = `${API}/alumnos/?`;
    if (filtroEstado  !== "all") url += `estado=${filtroEstado}&`;
    if (filtroCarrera !== "all") url += `carrera=${filtroCarrera}&`;
    if (filtroBusqueda)          url += `search=${encodeURIComponent(filtroBusqueda)}&`;

    const res = await authFetch(url);
    if (!res) return;
    const data = await res.json();
    if (!Array.isArray(data)) return;

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

    if (!pag.length) {
      tbody.innerHTML = `
        <tr>
          <td colspan="5" style="text-align:center;padding:3rem;color:var(--text-muted);">
            <span class="material-icons" style="font-size:2.5rem;display:block;margin-bottom:0.5rem;opacity:0.4;">person_off</span>
            Sin alumnos para mostrar.
          </td>
        </tr>`;
      mostrarPaginador();
      return;
    }

    pag.forEach(alumno => {
      const tr = document.createElement("tr");

      const carreras = alumno.carreras && alumno.carreras.length > 0
        ? alumno.carreras
        : [{ descripcion: alumno.carrera_nombre, color: alumno.carrera_color }];

      const estadoNombre = alumno.carreras && alumno.carreras.length > 0
        ? alumno.carreras[0].estado
        : alumno.estado_nombre;

      const esActivo = estadoNombre?.toLowerCase() === "activo";

      tr.style.cursor = "pointer";
      tr.dataset.id   = alumno.id_alumno;

      tr.innerHTML = `
        <td style="padding-right:0; width:48px;">${renderAvatar(alumno.nombre, alumno.apellido)}</td>
        <td>
          ${alumno.apellido}, ${alumno.nombre}
          <br><span style="font-size:0.78rem; color:var(--text-muted); font-weight:400;">DNI ${alumno.dni ?? ''}</span>
        </td>
        <td>${formatearChipCarreras(carreras)}</td>
        <td>${formatearChipEstado(estadoNombre)}</td>
        <td class="acciones-col">
          <div style="position:relative; display:inline-block;">
            <button class="btn-menu" data-id="${alumno.id_alumno}"
              style="background:none; border:none; cursor:pointer; padding:0.3rem 0.6rem;
                     border-radius:6px; color:#6b7280; font-size:1.4rem; line-height:1;
                     transition: background 0.15s;"
              onmouseenter="this.style.background='#f3f4f6'"
              onmouseleave="this.style.background='none'">
              ⋮
            </button>
            <div class="dropdown-menu-alumno hidden" data-id="${alumno.id_alumno}"
              style="position:fixed; background:#fff; border:1px solid #e5e7eb;
                     border-radius:10px; box-shadow:0 4px 20px rgba(0,0,0,0.12);
                     min-width:190px; z-index:1000; overflow:hidden; padding:4px 0;">

              <button class="menu-item btn-ver-ficha" data-id="${alumno.id_alumno}">
                <span class="material-icons" style="font-size:18px; color:#6b7280;">person</span>
                Ver ficha
              </button>

              <button class="menu-item btn-cobros" data-id="${alumno.id_alumno}">
                <span class="material-icons" style="font-size:18px; color:#6b7280;">payments</span>
                Ir a cobros
              </button>

              <button class="menu-item btn-editar" data-id="${alumno.id_alumno}">
                <span class="material-icons" style="font-size:18px; color:#6b7280;">edit</span>
                Editar datos
              </button>

              <button class="menu-item btn-agregar-carrera" data-id="${alumno.id_alumno}">
                <span class="material-icons" style="font-size:18px; color:#6b7280;">school</span>
                Agregar carrera
              </button>

              <div style="border-top:1px solid #e5e7eb; margin:4px 0;"></div>

              <button class="menu-item btn-cambiar-estado"
                data-id="${alumno.id_alumno}"
                data-estado="${estadoNombre}"
                style="color:${esActivo ? '#dc2626' : '#16a34a'}">
                <span class="material-icons" style="font-size:18px;">${esActivo ? 'block' : 'check_circle'}</span>
                ${esActivo ? 'Dar de baja' : 'Reactivar'}
              </button>

            </div>
          </div>
        </td>
      `;

      tbody.appendChild(tr);
    });

    document.querySelectorAll(".menu-item").forEach(item => {
      item.style.cssText = `
        display:flex; align-items:center; gap:0.7rem;
        width:100%; padding:0.55rem 1rem;
        background:none; border:none; cursor:pointer;
        font-size:0.88rem; color:#374151; text-align:left;
        transition:background 0.15s; font-family: inherit;
      `;
      item.addEventListener("mouseenter", () => item.style.background = "#f3f4f6");
      item.addEventListener("mouseleave", () => item.style.background = "none");
    });

    // Contador de resultados
    const contador = document.getElementById("contadorAlumnos");
    if (contador) {
      const total  = alumnosData.length;
      const desde  = total === 0 ? 0 : (paginaActual - 1) * POR_PAGINA + 1;
      const hasta  = Math.min(paginaActual * POR_PAGINA, total);
      contador.textContent = total > 0
        ? `Mostrando ${desde}–${hasta} de ${total} alumnos`
        : "";
    }

    mostrarPaginador();
  }

  // ===============================
  // CLICK EN FILA → ir a ficha
  // ===============================
  document.addEventListener("click", e => {
    const fila = e.target.closest("#tablaAlumnos tbody tr");
    if (!fila) return;
    // Si el click fue en el menú tres puntos o dentro del dropdown, no navegar
    if (e.target.closest(".btn-menu") || e.target.closest(".dropdown-menu-alumno")) return;
    const id = fila.dataset.id;
    if (id) window.location.href = `/alumnos/${id}/`;
  });

  // ===============================
  // MENÚ TRES PUNTOS
  // ===============================
  document.addEventListener("click", e => {
    if (!e.target.closest(".btn-menu") && !e.target.closest(".dropdown-menu-alumno")) {
      document.querySelectorAll(".dropdown-menu-alumno").forEach(m => m.classList.add("hidden"));
    }
  });

  document.addEventListener("click", e => {
    const btnMenu = e.target.closest(".btn-menu");
    if (!btnMenu) return;
    e.stopPropagation();

    const id       = btnMenu.dataset.id;
    const dropdown = document.querySelector(`.dropdown-menu-alumno[data-id="${id}"]`);

    document.querySelectorAll(".dropdown-menu-alumno").forEach(m => {
      if (m !== dropdown) m.classList.add("hidden");
    });

    if (dropdown.classList.contains("hidden")) {
      const rect = btnMenu.getBoundingClientRect();
      dropdown.style.top  = `${rect.bottom + window.scrollY + 4}px`;
      dropdown.style.left = `${rect.right - dropdown.offsetWidth + window.scrollX}px`;
      dropdown.classList.remove("hidden");

      requestAnimationFrame(() => {
        const dr = dropdown.getBoundingClientRect();
        if (dr.right > window.innerWidth) {
          dropdown.style.left = `${window.innerWidth - dr.width - 8 + window.scrollX}px`;
        }
        if (dr.bottom > window.innerHeight) {
          dropdown.style.top = `${rect.top + window.scrollY - dr.height - 4}px`;
        }
      });
    } else {
      dropdown.classList.add("hidden");
    }
  });

  document.addEventListener("click", e => {
    const btn = e.target.closest(".btn-ver-ficha");
    if (!btn) return;
    window.location.href = `/alumnos/${btn.dataset.id}/`;
  });

  document.addEventListener("click", e => {
    const btn = e.target.closest(".btn-cobros");
    if (!btn) return;
    window.location.href = `/cobros/cobros/?alumno=${btn.dataset.id}`;
  });

  document.addEventListener("click", e => {
    const btn = e.target.closest(".btn-editar");
    if (!btn) return;
    window.location.href = `/alumnos/alumnos/nuevo/?editar=${btn.dataset.id}`;
  });

  document.addEventListener("click", e => {
    const btn = e.target.closest(".btn-agregar-carrera");
    if (!btn) return;
    window.location.href = `/alumnos/alumnos/nuevo/?agregar_carrera=${btn.dataset.id}`;
  });

  document.addEventListener("click", async e => {
    const btn = e.target.closest(".btn-cambiar-estado");
    if (!btn) return;

    document.querySelectorAll(".dropdown-menu-alumno").forEach(m => m.classList.add("hidden"));

    const estadoActual = btn.dataset.estado?.toLowerCase();
    const esActivo     = estadoActual === "activo";
    const accion       = esActivo ? "dar de baja" : "reactivar";

    const ok = await showConfirm(`¿Querés ${accion} este alumno?`, "Confirmar");
    if (!ok) return;

    const r = await authFetch(`${API}/alumnos/${btn.dataset.id}/`, {
      method:  "PATCH",
      headers: { "Content-Type": "application/json" },
      body:    JSON.stringify({ id_estado: esActivo ? 2 : 1 }),
    });

    if (r && r.ok) cargarAlumnos();
  });

  // ===============================
  // PAGINADOR
  // ===============================
  function mostrarPaginador() {
    const cont = document.getElementById("paginador");
    if (!cont) return;
    cont.innerHTML = "";

    const total = Math.ceil(alumnosData.length / POR_PAGINA);
    if (total <= 1) return;

    function addBtn(label, page, activo = false) {
      const li  = document.createElement("li");
      if (activo) li.classList.add("active");
      const btn = document.createElement("a");
      btn.href        = "#";
      btn.textContent = label;
      btn.addEventListener("click", e => {
        e.preventDefault();
        paginaActual = page;
        mostrarPagina();
      });
      li.appendChild(btn);
      cont.appendChild(li);
    }

    function addEllipsis() {
      const li   = document.createElement("li");
      const span = document.createElement("span");
      span.textContent = "…";
      span.style.cssText = "padding:0 0.5rem; color:var(--text-muted); line-height:2rem; display:block;";
      li.appendChild(span);
      cont.appendChild(li);
    }

    // Páginas a mostrar: siempre primera y última + ventana de ±2 alrededor de la actual
    const visible = new Set([1, total]);
    for (let i = Math.max(1, paginaActual - 2); i <= Math.min(total, paginaActual + 2); i++) {
      visible.add(i);
    }
    const paginas = [...visible].sort((a, b) => a - b);

    // Anterior
    const liPrev = document.createElement("li");
    const aPrev  = document.createElement("a");
    aPrev.href        = "#";
    aPrev.textContent = "‹";
    aPrev.style.cssText = paginaActual === 1 ? "opacity:.35; pointer-events:none;" : "";
    aPrev.addEventListener("click", e => { e.preventDefault(); if (paginaActual > 1) { paginaActual--; mostrarPagina(); } });
    liPrev.appendChild(aPrev);
    cont.appendChild(liPrev);

    // Páginas con ellipsis
    let anterior = null;
    paginas.forEach(p => {
      if (anterior !== null && p - anterior > 1) addEllipsis();
      addBtn(String(p), p, p === paginaActual);
      anterior = p;
    });

    // Siguiente
    const liNext = document.createElement("li");
    const aNext  = document.createElement("a");
    aNext.href        = "#";
    aNext.textContent = "›";
    aNext.style.cssText = paginaActual === total ? "opacity:.35; pointer-events:none;" : "";
    aNext.addEventListener("click", e => { e.preventDefault(); if (paginaActual < total) { paginaActual++; mostrarPagina(); } });
    liNext.appendChild(aNext);
    cont.appendChild(liNext);
  }

  // ===============================
  // FILTROS
  // ===============================
  async function cargarFiltros() {
    try {
      const [resEstados, resCarreras] = await Promise.all([
        authFetch(`${API}/estados/`),
        authFetch(`${API}/carreras/`),
      ]);

      if (resEstados && resEstados.ok) {
        const estados = await resEstados.json();
        const sel = document.getElementById("filtroEstado");
        if (sel) {
          estados.forEach(e => {
            const opt = document.createElement("option");
            opt.value       = e.id_estado;
            opt.textContent = e.descripcion;
            sel.appendChild(opt);
          });
          sel.value = "1";  // pre-seleccionar Activo
        }
      }

      if (resCarreras && resCarreras.ok) {
        const carreras = await resCarreras.json();
        const sel = document.getElementById("filtroCarrera");
        if (sel) {
          carreras.forEach(c => {
            const opt = document.createElement("option");
            opt.value       = c.id_carrera;
            opt.textContent = c.descripcion;
            sel.appendChild(opt);
          });
        }
      }
    } catch (err) {
      console.error("Error cargando filtros:", err);
    }
  }

  document.getElementById("buscadorAlumno")?.addEventListener("input", e => {
    clearTimeout(searchTimeout);
    searchTimeout = setTimeout(() => {
      filtroBusqueda = e.target.value.trim();
      cargarAlumnos();
    }, 300);
  });

  document.getElementById("filtroEstado")?.addEventListener("change", e => {
    filtroEstado = e.target.value;
    cargarAlumnos();
  });

  document.getElementById("filtroCarrera")?.addEventListener("change", e => {
    filtroCarrera = e.target.value;
    cargarAlumnos();
  });

  // ===============================
  // INICIO
  // ===============================
  if (document.getElementById("tablaAlumnos")) {
    cargarFiltros();
    cargarAlumnos();
  }

});
