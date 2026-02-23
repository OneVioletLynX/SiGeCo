document.addEventListener("DOMContentLoaded", () => {
  const modal = document.getElementById("modalCarrera");
  const form = document.getElementById("formCarrera");
  const closeBtn = modal.querySelector(".close");
  const tabla = document.getElementById("tabla-carreras");
  const buttons = document.querySelectorAll(".action-button");
  const title = document.getElementById("modalCarreraTitle");

  let carreraSeleccionada = null;
  let isSubmitting = false;

  const ESTADOS_PALETA = {
  "activa":   { bg: "#E8F5E9", text: "#2E7D32" },
  "inactiva": { bg: "#FFEBEE", text: "#C62828" }
};

function formatearChipEstado(estado) {
  if (!estado) return "-";

  const c = ESTADOS_PALETA[estado.toLowerCase()] 
            || { bg:"#E0E0E0", text:"#424242" };

  return `
    <span class="chip" style="background:${c.bg}; color:${c.text}">
      <span class="dot" style="background:${c.text}"></span>
      ${estado}
    </span>
  `;
}

function formatearMoneda(valor) {
  if (!valor) return "—";
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
        <button class="btn-baja" data-id="${carrera.id_carrera}">
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
    modal.style.display = "block";
  }

  // ----------------------------------------------------------
  // Modal editar
  // ----------------------------------------------------------
  async function abrirModalEditar() {
    if (!carreraSeleccionada) {
      showAlert("Seleccioná una carrera para modificar.", "warning");
      return;
    }

    try {
      const response = await fetch(`http://localhost:8000/api/carreras/${carreraSeleccionada.id_carrera}/`);
      const carrera = await response.json();

      form.reset();
      document.getElementById("carreraId").value = carrera.id_carrera;
      document.getElementById("descripcion").value = carrera.descripcion;
      document.getElementById("inscripcion").value = carrera.inscripcion_vigente ?? "";
      document.getElementById("cuota").value = carrera.cuota_vigente ?? "";

      title.innerText = "Modificar Carrera";
      modal.style.display = "block";
    } catch (error) {
      console.error("Error al obtener carrera:", error);
      showAlert("No se pudo cargar la información de la carrera.", "error");
    }
  }

  // ----------------------------------------------------------
  // Dar de baja (PATCH)
  // ----------------------------------------------------------
  async function eliminarCarrera() {
    if (!carreraSeleccionada) {
      showAlert("Seleccioná una carrera para dar de baja.", "warning");
      return;
    }

    // Confirmación personalizada
    const ok = await showConfirm("¿Deseás marcar esta carrera como inactiva?", "Dar de baja");
    if (!ok) return;


    try {
      const response = await fetch(
        `http://localhost:8000/api/carreras/${carreraSeleccionada.id_carrera}/`,
        {
          method: "PATCH",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ id_estado: 2 }),
        }
      );

      if (response.ok) {
        const data = await response.json();
        showAlert(`Carrera marcada como ${data.nuevo_estado} ✅`, "success");

        const refreshed = await fetch(
          `http://localhost:8000/api/carreras/${carreraSeleccionada.id_carrera}/`
        );
        const updatedCarrera = await refreshed.json();

        carreraSeleccionada = updatedCarrera;
        actualizarTablaDerecha(updatedCarrera);

        const fila = document.querySelector(
          `#tabla-carreras tr[data-id="${updatedCarrera.id_carrera}"]`
        );
        if (fila) {
          const celdas = fila.querySelectorAll("td");
          celdas[0].textContent = updatedCarrera.descripcion;
          celdas[1].textContent = updatedCarrera.total_alumnos ?? 0;
          celdas[2].textContent = updatedCarrera.activos ?? 0;
          celdas[3].textContent = updatedCarrera.finalizados ?? 0;
          celdas[4].textContent = updatedCarrera.inactivos ?? 0;
        }
      } else {
        showAlert("Error al dar de baja la carrera.", "error");
      }
    } catch (error) {
      console.error("Error al dar de baja:", error);
      showAlert("Error de conexión con el servidor.", "error");
    }
  }

  // ----------------------------------------------------------
  // Guardar carrera (POST y PUT)
  // ----------------------------------------------------------
  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    if (isSubmitting) return;
    isSubmitting = true;

    const id = document.getElementById("carreraId").value;
    const data = {
      descripcion: document.getElementById("descripcion").value.trim(),
      inscripcion: parseFloat(document.getElementById("inscripcion").value),
      cuota: parseFloat(document.getElementById("cuota").value),
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
        showAlert(id ? "Carrera actualizada ✅" : "Carrera creada correctamente 🎉", "success");
        modal.style.display = "none";
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
  closeBtn.onclick = () => (modal.style.display = "none");
  window.onclick = (e) => {
    if (e.target === modal) modal.style.display = "none";
  };

  // ----------------------------------------------------------
  // Inicializar
  // ----------------------------------------------------------
  cargarCarreras();
});


document.addEventListener("click", e => {

  const btn = e.target.closest("button");
  if (!btn) return;

  const id = btn.dataset.id;

  if (btn.classList.contains("btn-editar")) {
    carreraSeleccionada = { id_carrera: id };
    abrirModalEditar();
  }

  if (btn.classList.contains("btn-baja")) {
    carreraSeleccionada = { id_carrera: id };
    eliminarCarrera();
  }

});