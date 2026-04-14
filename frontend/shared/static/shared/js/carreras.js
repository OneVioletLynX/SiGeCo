// ===========================
// AUTH — helper central
// ===========================
function getToken() {
  return localStorage.getItem("sigeco_access") || "";
}

async function authFetch(url, options = {}) {
  const token = getToken();
  if (!token) {
    window.location.href = "http://127.0.0.1:8001/";
    return;
  }

  const headers = {
    ...(options.headers || {}),
    "Authorization": `Bearer ${token}`,
  };

  const resp = await fetch(url, { ...options, headers });

  if (resp.status === 401) {
    localStorage.removeItem("sigeco_access");
    localStorage.removeItem("sigeco_refresh");
    localStorage.removeItem("sigeco_rol");
    window.location.href = "http://127.0.0.1:8001/";
    return;
  }

  return resp;
}

document.addEventListener("DOMContentLoaded", () => {

  // Redirigir si no hay token
  if (!getToken()) {
    window.location.href = "http://127.0.0.1:8001/";
    return;
  }

  const modal   = document.getElementById("modalCarrera");
  const form    = document.getElementById("formCarrera");
  const closeBtn = modal.querySelector(".close");
  const tabla   = document.getElementById("tabla-carreras");
  const buttons = document.querySelectorAll(".action-button");
  const title   = document.getElementById("modalCarreraTitle");

  let carreraSeleccionada = null;
  let isSubmitting        = false;

  function aclararColor(hex, porcentaje) {
    const num = parseInt(hex.replace("#", ""), 16);
    let r = (num >> 16) + porcentaje;
    let g = ((num >> 8) & 0x00ff) + porcentaje;
    let b = (num & 0x0000ff) + porcentaje;
    r = r > 255 ? 255 : r;
    g = g > 255 ? 255 : g;
    b = b > 255 ? 255 : b;
    return `rgb(${r}, ${g}, ${b})`;
  }

  const colorPicker      = document.getElementById("colorPicker");
  const hiddenColorInput = document.getElementById("colorCarrera");
  const chipPreview      = document.querySelector(".chip-demo");
  const nombreInput      = document.getElementById("descripcion");

  const COLORES_CARRERA = [
    "#1E3A8A", "#0F766E", "#166534", "#7C2D12",
    "#9A3412", "#0c1332", "#831843", "#1F2937",
    "#374151", "#B91C1C",
  ];

  let colorSeleccionado = COLORES_CARRERA[0];

  function renderColorPicker() {
    COLORES_CARRERA.forEach(color => {
      const div = document.createElement("div");
      div.classList.add("color-option");
      div.style.backgroundColor = color;
      div.dataset.color = color;
      if (color === colorSeleccionado) div.classList.add("selected");

      div.addEventListener("click", () => {
        document.querySelectorAll(".color-option").forEach(o => o.classList.remove("selected"));
        div.classList.add("selected");
        colorSeleccionado      = color;
        hiddenColorInput.value = color;
        actualizarPreview();
      });

      colorPicker.appendChild(div);
    });
  }

  function actualizarPreview() {
    const fondoClaro = aclararColor(colorSeleccionado, 150);
    chipPreview.style.backgroundColor = fondoClaro;
    chipPreview.style.color           = colorSeleccionado;
    chipPreview.innerHTML = `
      <span class="dot" style="background:${colorSeleccionado}"></span>
      ${nombreInput.value || "Nombre"}
    `;
  }

  renderColorPicker();
  actualizarPreview();
  nombreInput.addEventListener("input", actualizarPreview);

  function resetFormularioCarrera() {
    form.reset();
    clearAllErrors();
    isSubmitting = false;
  }

  function setError(inputId, message) {
    document.getElementById(inputId).style.border         = "1px solid #e74c3c";
    document.getElementById("error-" + inputId).textContent = message;
  }

  function clearError(inputId) {
    document.getElementById(inputId).style.border           = "1px solid #D9D9D9";
    document.getElementById("error-" + inputId).textContent = "";
  }

  function clearAllErrors() {
    ["descripcion", "inscripcion", "cuota"].forEach(clearError);
  }

  function formatearChipEstado(estado) {
    if (!estado) return "-";
    const estadoLower = estado.toLowerCase();
    return `
      <span class="chip chip-${estadoLower}">
        <span class="dot"></span>
        ${estado}
      </span>
    `;
  }

  function formatearMoneda(valor) {
    if (valor === null || valor === undefined) return "—";
    return `$${Number(valor).toLocaleString("es-AR")}`;
  }

  // -------------------------------------------------------
  // Cargar carreras
  // -------------------------------------------------------
  async function cargarCarreras() {
    try {
      const response = await authFetch("http://localhost:8000/api/carreras/");
      if (!response) return;
      let carreras = await response.json();
      carreras = carreras.results || carreras;

      tabla.innerHTML = "";

      carreras.forEach(carrera => {
        const tr = document.createElement("tr");
        tr.dataset.id = carrera.id_carrera;
        tr.innerHTML = `
          <td>${carrera.descripcion}</td>
          <td>${formatearChipEstado(carrera.estado_actual)}</td>
          <td>${formatearMoneda(carrera.cuota_vigente)}</td>
          <td>${formatearMoneda(carrera.inscripcion_vigente)}</td>
          <td class="acciones-col">
            <div class="acciones">
              <button class="btn-editar" data-id="${carrera.id_carrera}">
                <img src="/static/shared/assets/edit.svg">
              </button>
              <button class="btn-baja" data-id="${carrera.id_carrera}" data-estado="${carrera.estado_actual}">
                <img src="/static/shared/assets/remove.svg">
              </button>
            </div>
          </td>
        `;
        tabla.appendChild(tr);
      });

    } catch (error) {
      console.error("Error cargando carreras:", error);
      showAlert("Error al cargar las carreras.", "error");
    }
  }

  // -------------------------------------------------------
  // Modal nuevo
  // -------------------------------------------------------
  function abrirModalNueva() {
    form.reset();
    document.getElementById("carreraId").value = "";
    title.innerText = "Nueva Carrera";

    colorSeleccionado      = COLORES_CARRERA[0];
    hiddenColorInput.value = colorSeleccionado;
    document.querySelectorAll(".color-option").forEach(o => o.classList.remove("selected"));
    document.querySelector(".color-option").classList.add("selected");
    actualizarPreview();
    modal.style.display = "block";
  }

  // -------------------------------------------------------
  // Modal editar
  // -------------------------------------------------------
  async function abrirModalEditar(id) {
    try {
      const response = await authFetch(`http://localhost:8000/api/carreras/${id}/`);
      if (!response) return;
      const carrera = await response.json();

      form.reset();
      document.getElementById("carreraId").value   = carrera.id_carrera;
      document.getElementById("descripcion").value = carrera.descripcion;
      document.getElementById("inscripcion").value = carrera.inscripcion_vigente ?? "";
      document.getElementById("cuota").value       = carrera.cuota_vigente ?? "";

      hiddenColorInput.value = carrera.color;
      colorSeleccionado      = carrera.color;

      document.querySelectorAll(".color-option").forEach(o => {
        o.classList.remove("selected");
        if (o.dataset.color === carrera.color) o.classList.add("selected");
      });

      actualizarPreview();
      title.innerText     = "Modificar Carrera";
      modal.style.display = "block";

    } catch (error) {
      console.error("Error al obtener carrera:", error);
      showAlert("No se pudo cargar la carrera.", "error");
    }
  }

  // -------------------------------------------------------
  // Cambiar estado (PATCH)
  // -------------------------------------------------------
  async function eliminarCarrera(id, estadoActual) {
    if (!estadoActual) return;

    const nuevoEstado = estadoActual.toLowerCase() === "activo" ? 2 : 1;
    const ok = await showConfirm("¿Deseás cambiar el estado de esta carrera?", "Cambiar estado");
    if (!ok) return;

    try {
      const response = await authFetch(`http://localhost:8000/api/carreras/${id}/`, {
        method:  "PATCH",
        headers: { "Content-Type": "application/json" },
        body:    JSON.stringify({ id_estado: nuevoEstado }),
      });

      if (response && response.ok) {
        showAlert("Estado actualizado correctamente ✅", "success");
        await cargarCarreras();
      } else {
        showAlert("No se pudo actualizar el estado.", "error");
      }
    } catch (error) {
      showAlert("Error de conexión.", "error");
    }
  }

  // -------------------------------------------------------
  // Guardar carrera (POST / PUT)
  // -------------------------------------------------------
  form.addEventListener("submit", async e => {
    e.preventDefault();
    if (isSubmitting) return;

    clearAllErrors();
    let hayErrores = false;

    const descripcion = document.getElementById("descripcion").value.trim();
    const inscripcion = document.getElementById("inscripcion").value;
    const cuota       = document.getElementById("cuota").value;

    if (descripcion.length < 3)            { setError("descripcion", "Debe tener al menos 3 caracteres"); hayErrores = true; }
    if (!inscripcion || parseFloat(inscripcion) <= 0) { setError("inscripcion", "Debe ser mayor a 0");   hayErrores = true; }
    if (!cuota || parseFloat(cuota) <= 0)  { setError("cuota", "Debe ser mayor a 0");                    hayErrores = true; }

    if (hayErrores) return;

    isSubmitting = true;

    const id     = document.getElementById("carreraId").value;
    const data   = {
      descripcion,
      inscripcion: parseFloat(inscripcion),
      cuota:       parseFloat(cuota),
      color:       document.getElementById("colorCarrera").value,
    };
    const method = id ? "PUT"  : "POST";
    const url    = id ? `http://localhost:8000/api/carreras/${id}/` : "http://localhost:8000/api/carreras/";

    try {
      const response = await authFetch(url, {
        method,
        headers: { "Content-Type": "application/json" },
        body:    JSON.stringify(data),
      });

      if (response && response.ok) {
        showAlert(id ? "Carrera actualizada ✅" : "Carrera creada correctamente 🎉", "success");
        modal.style.display = "none";
        resetFormularioCarrera();
        await cargarCarreras();
      } else {
        showAlert("Error al guardar la carrera.", "error");
      }
    } catch (error) {
      showAlert("No se pudo conectar con el servidor.", "error");
    } finally {
      isSubmitting = false;
    }
  });

  // -------------------------------------------------------
  // Cerrar modal
  // -------------------------------------------------------
  closeBtn.onclick = () => { modal.style.display = "none"; resetFormularioCarrera(); };
  window.onclick   = e => {
    if (e.target === modal) { modal.style.display = "none"; resetFormularioCarrera(); }
  };

  // -------------------------------------------------------
  // Acciones por fila
  // -------------------------------------------------------
  document.addEventListener("click", e => {
    const btn = e.target.closest("button");
    if (!btn) return;
    const id = btn.dataset.id;
    if (!id) return;
    if (btn.classList.contains("btn-editar")) abrirModalEditar(id);
    if (btn.classList.contains("btn-baja"))   eliminarCarrera(id, btn.dataset.estado);
  });

  // -------------------------------------------------------
  // Inicializar
  // -------------------------------------------------------
  cargarCarreras();
});