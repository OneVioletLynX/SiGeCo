document.addEventListener("DOMContentLoaded", () => {

  const form = document.getElementById("alumnoForm");

  let isSubmitting = false;

  // ==========================================================
  //  FILTROS
  // ==========================================================
  let filtroEstado = "all";
  let filtroCarrera = "all";
  let filtroBusqueda = "";
  let searchTimeout = null;
function aclararColor(hex, factor = 150) {
  hex = hex.replace("#", "");
  const r = Math.min(255, parseInt(hex.substring(0, 2), 16) + factor);
  const g = Math.min(255, parseInt(hex.substring(2, 4), 16) + factor);
  const b = Math.min(255, parseInt(hex.substring(4, 6), 16) + factor);
  return `rgb(${r},${g},${b})`;
}

function formatearChipCarrera(nombre, color) {
  if (!nombre) return "-";
  if (!color) return nombre;

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
    "baja":     { bg: "#FFF3E0", text: "#EF6C00" }
  };

  function formatearChipEstado(estado) {
    if (!estado) return "-";
    const c = ESTADOS_PALETA[estado.toLowerCase()] || { bg:"#E0E0E0", text:"#424242" };
    return `
      <span class="chip" style="background:${c.bg}; color:${c.text}">
        <span class="dot" style="background:${c.text}"></span>
        ${estado}
      </span>
    `;
  }

  // ==========================================================
  //  VALIDACIONES - UTILIDADES
  // ==========================================================
  function limpiarErroresAlumno() {
    document.querySelectorAll(".error-msg").forEach(e => (e.innerText = ""));
  }

  function setError(name, msg) {
    const span = document.getElementById("error-" + name);
    if (span) span.innerText = msg;
  }

  // ==========================================================
  //  VALIDACIÓN COMPLETA (al guardar)
  // ==========================================================
  function validarFormularioAlumno() {
    limpiarErroresAlumno();
    let valido = true;
    const f = form;

    const dniVal = f.dni.value.trim();
    const emailVal = f.email.value.trim();
    const legajoVal = f.legajo.value.trim();

    // STEP 1
    if (!f.nombre.value.trim()) { setError("nombre", "El nombre es obligatorio."); valido = false; }
    if (!f.apellido.value.trim()) { setError("apellido", "El apellido es obligatorio."); valido = false; }

    if (!/^[0-9]{7,8}$/.test(dniVal)) {
      setError("dni", "El DNI debe tener 7 u 8 dígitos.");
      valido = false;
    }

    if (!f.fecha_nacimiento.value) {
      setError("fecha_nacimiento", "La fecha es obligatoria.");
      valido = false;
    }

    // STEP 2
    if (!f.ciudad.value) { setError("ciudad", "Seleccione una localidad."); valido = false; }
    if (!f.direccion.value.trim()) { setError("direccion", "Dirección obligatoria."); valido = false; }
    if (!f.numero.value || Number(f.numero.value) <= 0) { setError("numero", "Altura inválida."); valido = false; }

    if (!/^[0-9]{2,5}$/.test(f.prefijo.value.trim())) {
      setError("prefijo", "Prefijo inválido.");
      valido = false;
    }

    if (!/^[0-9]{6,15}$/.test(f.telefono.value.trim())) {
      setError("telefono", "Teléfono inválido.");
      valido = false;
    }

    if (!emailVal) {
      setError("email", "El correo es obligatorio.");
      valido = false;
    } else if (!/^\S+@\S+\.\S+$/.test(emailVal)) {
      setError("email", "Correo inválido.");
      valido = false;
    }

    // STEP 3
    if (legajoVal && !/^[A-Za-z0-9\-]+$/.test(legajoVal)) {
      setError("legajo", "Legajo inválido.");
      valido = false;
    }

    if (!f.id_estado.value) { setError("id_estado", "Seleccione un estado."); valido = false; }
    if (!f.id_carrera.value) { setError("id_carrera", "Seleccione una carrera."); valido = false; }

    if (!f.anio_ingreso.value) {
      setError("anio_ingreso", "Seleccione el año.");
      valido = false;
    }

    return valido;
  }

  // ==========================================================
  //  MULTI-STEP
  // ==========================================================

  // ==========================================================
  //  MODO LECTURA / EDICIÓN
  // ==========================================================
  function setReadOnlyMode(enabled) {
    const inputs = form.querySelectorAll("input, select, textarea");

    inputs.forEach(el => {
      el.disabled = !!enabled;
      el.classList.toggle("readonly", enabled);
    });

    // ❌ NUNCA tocar el botón guardar desde acá
  }



  // ==========================================================
  //  BAJA ALUMNO (con confirm personalizado)
  // ==========================================================
  async function darDeBajaAlumno(id) {

    const ok = await showConfirm("¿Seguro que deseas dar de baja este alumno?", "Confirmar operación");
    if (!ok) return;

    try {
      const r = await fetch(`http://localhost:8000/api/alumnos/${id}/`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ id_estado: 2 })
      });

      if (r.ok) {
        showAlert("Alumno dado de baja correctamente", "success");
        cargarAlumnos();
      } else {
        showAlert("No fue posible dar de baja al alumno", "error");
      }

    } catch (e) {
      console.error(e);
      showAlert("Error de conexión con el servidor", "error");
    }
  }


  // ==========================================================
  //  TABLA + PAGINACIÓN
  // ==========================================================
  let alumnosData = [];
  let paginaActual = 1;
  const POR_PAGINA = 10;

  async function cargarAlumnos() {
    let url = "http://localhost:8000/api/alumnos/?";

    if (filtroEstado !== "all") url += `estado=${filtroEstado}&`;
    if (filtroCarrera !== "all") url += `carrera=${filtroCarrera}&`;
    if (filtroBusqueda) url += `search=${encodeURIComponent(filtroBusqueda)}&`;

    const res = await fetch(url);
    alumnosData = await res.json();

    paginaActual = 1;
    mostrarPagina();
  }

  function mostrarPagina() {
    const tbody = document.querySelector("#tablaAlumnos tbody");
    tbody.innerHTML = "";

    const inicio = (paginaActual - 1) * POR_PAGINA;
    const pag = alumnosData.slice(inicio, inicio + POR_PAGINA);

    pag.forEach(alumno => {
      const tr = document.createElement("tr");

      tr.innerHTML = `
        <td>${alumno.apellido}, ${alumno.nombre}</td>
        <td>${formatearChipCarrera(alumno.carrera_nombre, alumno.carrera_color)}</td>
        <td>${formatearChipEstado(alumno.estado_nombre)}</td>
        <td class="acciones-col">

          <div class="acciones">
            <button class="btn-editar" data-id="${alumno.id_alumno}">
              <img src="/static/shared/assets/edit.svg">
            </button>
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
    cont.innerHTML = "";

    const total = Math.ceil(alumnosData.length / POR_PAGINA);
    if (total <= 1) return;

    function addBtn(label, page, disabled = false, isActive = false) {
      const li = document.createElement("li");
      li.classList.add("ulpgcds-pager__item");
      if (isActive) li.classList.add("ulpgcds-pager__item--is-active");

      const btn = document.createElement("a");
      btn.href = "#";
      btn.classList.add("pagination__link");
      btn.textContent = label;

      if (!disabled) {
        btn.addEventListener("click", e => {
          e.preventDefault();
          paginaActual = page;
          mostrarPagina();
        });
      } else {
        btn.classList.add("disabled");
      }

      li.appendChild(btn);
      cont.appendChild(li);
    }

    addBtn("<", paginaActual - 1, paginaActual === 1);
    for (let i = 1; i <= total; i++) addBtn(i, i, false, paginaActual === i);
    addBtn(">", paginaActual + 1, paginaActual === total);
  }

  document.addEventListener("click", e => {
    const btn = e.target.closest("button");
    if (!btn) return;
    const id = btn.dataset.id;

    if (btn.classList.contains("btn-editar")) abrirModalEditar(id);
    if (btn.classList.contains("btn-baja")) darDeBajaAlumno(id);
  });

  // ==========================================================
  //  FILTROS
  // ==========================================================
  document.getElementById("filtroEstado").addEventListener("change", e => {
    filtroEstado = e.target.value;
    cargarAlumnos();
  });

  document.getElementById("filtroCarrera").addEventListener("change", e => {
    filtroCarrera = e.target.value;
    cargarAlumnos();
  });

  document.getElementById("buscadorAlumno").addEventListener("input", e => {
    clearTimeout(searchTimeout);
    filtroBusqueda = e.target.value.trim();
    searchTimeout = setTimeout(() => cargarAlumnos(), 300);
  });

  // ==========================================================
  //  SELECTS
  // ==========================================================
  async function cargarCarreras() {
    const sel = document.getElementById("filtroCarrera");
    const res = await fetch("http://localhost:8000/api/carreras/");
    const carreras = await res.json();
    carreras.forEach(c => {
      sel.innerHTML += `<option value="${c.id_carrera}">${c.descripcion}</option>`;
    });
  }

  async function cargarEstados() {
    const sel = document.getElementById("filtroEstado");
    sel.innerHTML = `<option value="all" selected>Todos</option>`;
    const res = await fetch("http://localhost:8000/api/estados/");
    const estados = await res.json();
    estados.forEach(e => {
      sel.innerHTML += `<option value="${e.id_estado}">${e.descripcion}</option>`;
    });
  }

  async function cargarCarrerasForm() {
    const sel = document.getElementById("id_carrera");
    sel.innerHTML = `<option value="" disabled selected>Seleccione una carrera</option>`;
    const res = await fetch("http://localhost:8000/api/carreras/");
    const carreras = await res.json();
    carreras.forEach(c => {
      sel.innerHTML += `<option value="${c.id_carrera}">${c.descripcion}</option>`;
    });
  }

  async function cargarEstadosForm() {
    const sel = document.getElementById("id_estado");
    sel.innerHTML = `<option value="" disabled selected>Seleccione un estado</option>`;
    const res = await fetch("http://localhost:8000/api/estados/");
    const estados = await res.json();
    estados.forEach(e => {
      sel.innerHTML += `<option value="${e.id_estado}">${e.descripcion}</option>`;
    });
  }

  // ==========================================================
  //  ENVÍO DEL FORMULARIO (FIX DEL UPDATE)
  // ==========================================================
 if (form) {
  form.addEventListener("submit", async e => {
    e.preventDefault();
    if (isSubmitting) return;
    isSubmitting = true;

    const esValido = validarFormularioAlumno();
    if (!esValido) {
      isSubmitting = false;
      return;
    }

    const data = Object.fromEntries(new FormData(form));

    // 🔥 Fix crítico: convertir selects a número
    data.id_carrera = parseInt(data.id_carrera || "0");
    data.id_estado = parseInt(data.id_estado || "0");

    const id = form.dataset.editingId;
    const method = id ? "PUT" : "POST";
    const url = id
      ? `http://localhost:8000/api/alumnos/${id}/`
      : `http://localhost:8000/api/alumnos/`;

    try {
      const response = await fetch(url, {
        method,
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data)
      });

        if (response.ok) {
          const mensaje = id ? "Alumno modificado correctamente" : "Alumno creado correctamente";
          showAlert(mensaje, "success");
          
          form.reset();
          delete form.dataset.editingId;
          await cargarAlumnos();
        }
        else {
        const raw = await response.clone().text();
        console.log("🔍 Backend dijo:", raw);

        const err = await response.json().catch(() => null);
        limpiarErroresAlumno();

        if (err) {
          isSubmitting = false;
          return;
        }
      }

    } catch (e) {
      console.error("Error de conexión:", e);
    }

    isSubmitting = false;
  });
  }

  // ==========================================================
  //  INICIO
  // ==========================================================
  (async () => {
    await Promise.all([cargarCarreras(), cargarEstados()]);
    await cargarAlumnos();
  })();

});

