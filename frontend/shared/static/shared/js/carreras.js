document.addEventListener("DOMContentLoaded", () => {
  const modal = document.getElementById("modalCarrera");
  const form = document.getElementById("formCarrera");
  const closeBtn = modal.querySelector(".close");
  const tabla = document.getElementById("tabla-carreras");
  const buttons = document.querySelectorAll(".action-button");
  const title = document.getElementById("modalCarreraTitle");

  let carreraSeleccionada = null;
  let isSubmitting = false;
;

function aclararColor(hex, porcentaje) {
  const num = parseInt(hex.replace("#", ""), 16);
  let r = (num >> 16) + porcentaje;
  let g = ((num >> 8) & 0x00FF) + porcentaje;
  let b = (num & 0x0000FF) + porcentaje;

  r = r > 255 ? 255 : r;
  g = g > 255 ? 255 : g;
  b = b > 255 ? 255 : b;

  return `rgb(${r}, ${g}, ${b})`;
}

const colorPicker = document.getElementById("colorPicker");
const hiddenColorInput = document.getElementById("colorCarrera");
const chipPreview = document.querySelector(".chip-demo");
const nombreInput = document.getElementById("descripcion");

const COLORES_CARRERA = [
  "#1E3A8A",
  "#0F766E",
  "#166534",
  "#7C2D12",
  "#9A3412",
  "#0c1332",
  "#831843",
  "#1F2937",
  "#374151",
  "#B91C1C"
];

let colorSeleccionado = COLORES_CARRERA[0];

function renderColorPicker() {
  COLORES_CARRERA.forEach(color => {
    const div = document.createElement("div");
    div.classList.add("color-option");
    div.style.backgroundColor = color;
    div.dataset.color = color;

    if (color === colorSeleccionado) {
      div.classList.add("selected");
    }

    div.addEventListener("click", () => {
      document.querySelectorAll(".color-option")
        .forEach(o => o.classList.remove("selected"));

      div.classList.add("selected");

      colorSeleccionado = color;
      hiddenColorInput.value = color;

      actualizarPreview();
    });

    colorPicker.appendChild(div);
  });
}

function actualizarPreview() {
  const fondoClaro = aclararColor(colorSeleccionado, 150);

  chipPreview.style.backgroundColor = fondoClaro;
  chipPreview.style.color = colorSeleccionado;

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
  const input = document.getElementById(inputId);
  const error = document.getElementById("error-" + inputId);

  input.style.border = "1px solid #e74c3c";
  error.textContent = message;
}

function clearError(inputId) {
  const input = document.getElementById(inputId);
  const error = document.getElementById("error-" + inputId);

  input.style.border = "1px solid #D9D9D9";
  error.textContent = "";
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

  // ----------------------------------------------------------
  // Cargar carreras
  // ----------------------------------------------------------
  async function cargarCarreras() {
    try {
      const response = await fetch("http://localhost:8000/api/carreras/");
      let carreras = await response.json();

      carreras = carreras.results || carreras;

tabla.innerHTML = "";

carreras.forEach((carrera) => {

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

  // ----------------------------------------------------------
  // Seleccionar fila
  // ----------------------------------------------------------
  function seleccionarCarrera(tr, carrera) {
    document.querySelectorAll("#tabla-carreras tr").forEach(row => row.classList.remove("selected"));
    tr.classList.add("selected");
    carreraSeleccionada = carrera;
    actualizarTablaDerecha(carrera);
  }

  // ----------------------------------------------------------
  // Actualizar tabla de la derecha
  // ----------------------------------------------------------
  function actualizarTablaDerecha(carrera) {
    const valorCuota = document.getElementById("valorCuota");
    const valorInscripcion = document.getElementById("valorInscripcion");
    const estadoCarrera = document.getElementById("estadoCarrera");

    valorCuota.textContent = carrera.cuota_vigente
      ? `$${carrera.cuota_vigente.toLocaleString()}`
      : "—";

    valorInscripcion.textContent = carrera.inscripcion_vigente
      ? `$${carrera.inscripcion_vigente.toLocaleString()}`
      : "—";

    estadoCarrera.textContent = carrera.estado_actual ?? "—";
  }

  // ----------------------------------------------------------
  // Modal nuevo
  // ----------------------------------------------------------
function abrirModalNueva() {
  form.reset();
  document.getElementById("carreraId").value = "";
  title.innerText = "Nueva Carrera";

  // 🔥 Setear color por defecto
  colorSeleccionado = COLORES_CARRERA[0];
  hiddenColorInput.value = colorSeleccionado;

  document.querySelectorAll(".color-option")
    .forEach(o => o.classList.remove("selected"));

  document.querySelector(".color-option").classList.add("selected");

  actualizarPreview();

  modal.style.display = "block";
}

  // ----------------------------------------------------------
  // Modal editar
  // ----------------------------------------------------------
async function abrirModalEditar(id) {

  try {
    const response = await fetch(
      `http://localhost:8000/api/carreras/${id}/`
    );

    const carrera = await response.json();

    form.reset();

    document.getElementById("carreraId").value = carrera.id_carrera;
    document.getElementById("descripcion").value = carrera.descripcion;
    document.getElementById("inscripcion").value =
      carrera.inscripcion_vigente ?? "";
    document.getElementById("cuota").value =
      carrera.cuota_vigente ?? "";

      hiddenColorInput.value = carrera.color;
    colorSeleccionado = carrera.color;

  document.querySelectorAll(".color-option")
    .forEach(o => {
      o.classList.remove("selected");
      if (o.dataset.color === carrera.color) {
        o.classList.add("selected");
      }
    });

actualizarPreview();
    title.innerText = "Modificar Carrera";
    modal.style.display = "block";

  } catch (error) {
    console.error("Error al obtener carrera:", error);
    showAlert("No se pudo cargar la carrera.", "error");
  }
}

  // ----------------------------------------------------------
  // Dar de baja (PATCH)
  // ----------------------------------------------------------
async function eliminarCarrera(id, estadoActual) {

  if (!estadoActual) {
    console.error("Estado no definido");
    return;
  }

  const nuevoEstado = estadoActual.toLowerCase() === "activo" ? 2 : 1;

  const ok = await showConfirm(
    "¿Deseás cambiar el estado de esta carrera?",
    "Cambiar estado"
  );

  if (!ok) return;

  try {
    const response = await fetch(
      `http://localhost:8000/api/carreras/${id}/`,
      {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          id_estado: nuevoEstado
        }),
      }
    );

    if (response.ok) {
      showAlert("Estado actualizado correctamente ✅", "success");
      await cargarCarreras();
    } else {
      showAlert("No se pudo actualizar el estado.", "error");
    }

  } catch (error) {
    console.error("Error:", error);
    showAlert("Error de conexión.", "error");
  }
}

// ----------------------------------------------------------
// Guardar carrera (POST y PUT) con validaciones visuales
// ----------------------------------------------------------
form.addEventListener("submit", async (e) => {
  e.preventDefault();

  if (isSubmitting) return;

  const descripcionInput = document.getElementById("descripcion");
  const inscripcionInput = document.getElementById("inscripcion");
  const cuotaInput = document.getElementById("cuota");

  const descripcion = descripcionInput.value.trim();
  const inscripcion = inscripcionInput.value;
  const cuota = cuotaInput.value;

  // -------------------------
  // LIMPIAR ERRORES
  // -------------------------
  clearAllErrors();

  let hayErrores = false;

  // -------------------------
  // VALIDACIONES
  // -------------------------

  if (descripcion.length < 3) {
    setError("descripcion", "Debe tener al menos 3 caracteres");
    hayErrores = true;
  }

  if (!inscripcion || parseFloat(inscripcion) <= 0) {
    setError("inscripcion", "Debe ser mayor a 0");
    hayErrores = true;
  }

  if (!cuota || parseFloat(cuota) <= 0) {
    setError("cuota", "Debe ser mayor a 0");
    hayErrores = true;
  }

  if (hayErrores) return;

  // -------------------------
  // SI TODO OK → CONTINÚA
  // -------------------------

  isSubmitting = true;

  const id = document.getElementById("carreraId").value;

  const data = {
    descripcion: descripcion,
    inscripcion: parseFloat(inscripcion),
    cuota: parseFloat(cuota),
    color: document.getElementById("colorCarrera").value
  };

  const method = id ? "PUT" : "POST";
  const url = id
    ? `http://localhost:8000/api/carreras/${id}/`
    : `http://localhost:8000/api/carreras/`;

  try {
    const response = await fetch(url, {
      method,
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    });

    if (response.ok) {
      showAlert(
        id ? "Carrera actualizada ✅" : "Carrera creada correctamente 🎉",
        "success"
      );
modal.style.display = "none";
resetFormularioCarrera();
await cargarCarreras();
    } else {
      const err = await response.json();
      console.error(err);
      showAlert("Error al guardar la carrera.", "error");
    }
  } catch (error) {
    console.error("Error de red:", error);
    showAlert("No se pudo conectar con el servidor.", "error");
  } finally {
    isSubmitting = false;
  }
});

  // ----------------------------------------------------------
  // Botones
  // ----------------------------------------------------------
  buttons.forEach((btn) => {
    const text = btn.querySelector(".text").innerText.trim();
    if (text === "Alta") btn.addEventListener("click", abrirModalNueva);
    if (text === "Modificacion") btn.addEventListener("click", abrirModalEditar);
    if (text === "Baja") btn.addEventListener("click", eliminarCarrera);
  });

  // ----------------------------------------------------------
  // Cerrar modal
  // ----------------------------------------------------------
closeBtn.onclick = () => {
  modal.style.display = "none";
  resetFormularioCarrera();
};

window.onclick = (e) => {
  if (e.target === modal) {
    modal.style.display = "none";
    resetFormularioCarrera();
  }
};

  // ----------------------------------------------------------
  // Inicializar
  // ----------------------------------------------------------
  cargarCarreras();

  // ----------------------------------------------------------
// Acciones por fila (editar / eliminar)
// ----------------------------------------------------------
document.addEventListener("click", e => {

  const btn = e.target.closest("button");
  if (!btn) return;

  const id = btn.dataset.id;
  if (!id) return;

if (btn.classList.contains("btn-editar")) {
  abrirModalEditar(id);
}

if (btn.classList.contains("btn-baja")) {
  eliminarCarrera(id, btn.dataset.estado);
}

});
});

