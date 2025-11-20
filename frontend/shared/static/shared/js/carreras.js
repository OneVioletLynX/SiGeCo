document.addEventListener("DOMContentLoaded", () => {
  const modal = document.getElementById("modalCarrera");
  const form = document.getElementById("formCarrera");
  const closeBtn = modal.querySelector(".close");
  const tabla = document.getElementById("tabla-carreras");
  const buttons = document.querySelectorAll(".action-button");
  const title = document.getElementById("modalCarreraTitle");

  let carreraSeleccionada = null;
  let isSubmitting = false;

  // ----------------------------------------------------------
  // Cargar carreras
  // ----------------------------------------------------------
  async function cargarCarreras() {
    try {
      const response = await fetch("http://localhost:8000/api/carreras/");
      const carreras = await response.json();

      tabla.innerHTML = "";

      carreras.forEach((carrera, index) => {
        const tr = document.createElement("tr");
        tr.dataset.id = carrera.id_carrera;
        tr.innerHTML = `
          <td>${carrera.descripcion}</td>
          <td>${carrera.total_alumnos ?? 0}</td>
          <td>${carrera.activos ?? 0}</td>
          <td>${carrera.finalizados ?? 0}</td>
          <td>${carrera.inactivos ?? 0}</td>
        `;
        tr.addEventListener("click", () => seleccionarCarrera(tr, carrera));
        tabla.appendChild(tr);

        // 🔹 Seleccionar automáticamente la primera carrera
        if (index === 0) {
          tr.classList.add("selected");
          carreraSeleccionada = carrera;
          actualizarTablaDerecha(carrera);
        }
      });
    } catch (error) {
      console.error("Error cargando carreras:", error);
      alert("Error al cargar las carreras.");
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
  // Actualizar tabla de la derecha (valores vigentes)
  // ----------------------------------------------------------
  function actualizarTablaDerecha(carrera) {
    const valorCuota = document.getElementById("valorCuota");
    const valorInscripcion = document.getElementById("valorInscripcion");
    const estadoCarrera = document.getElementById("estadoCarrera");

    if (valorCuota)
      valorCuota.textContent = carrera.cuota_vigente
        ? `$${carrera.cuota_vigente.toLocaleString()}`
        : "—";

    if (valorInscripcion)
      valorInscripcion.textContent = carrera.inscripcion_vigente
        ? `$${carrera.inscripcion_vigente.toLocaleString()}`
        : "—";

    if (estadoCarrera)
      estadoCarrera.textContent = carrera.estado_actual ?? "—";
  }

  // ----------------------------------------------------------
  // Abrir modal para nueva carrera
  // ----------------------------------------------------------
  function abrirModalNueva() {
    form.reset();
    document.getElementById("carreraId").value = "";
    title.innerText = "Nueva Carrera";
    modal.style.display = "block";
  }

  // ----------------------------------------------------------
  // Abrir modal para editar
  // ----------------------------------------------------------
  async function abrirModalEditar() {
    if (!carreraSeleccionada) {
      alert("Seleccioná una carrera para modificar.");
      return;
    }

    try {
      const response = await fetch(
        `http://localhost:8000/api/carreras/${carreraSeleccionada.id_carrera}/`
      );
      const carrera = await response.json();

      form.reset();
      document.getElementById("carreraId").value = carrera.id_carrera;
      document.getElementById("descripcion").value = carrera.descripcion;
      document.getElementById("inscripcion").value =
        carrera.inscripcion_vigente ?? "";
      document.getElementById("cuota").value =
        carrera.cuota_vigente ?? "";

      title.innerText = "Modificar Carrera";
      modal.style.display = "block";
    } catch (error) {
      console.error("Error al obtener carrera:", error);
      alert("No se pudo cargar la información de la carrera.");
    }
  }

  // ----------------------------------------------------------
  // Baja carrera (cambia estado a Inactiva y refresca tablas)
  // ----------------------------------------------------------
  async function eliminarCarrera() {
    if (!carreraSeleccionada) {
      alert("Seleccioná una carrera para dar de baja.");
      return;
    }

    if (!confirm("¿Deseás marcar esta carrera como inactiva?")) return;

    try {
      const response = await fetch(
        `http://localhost:8000/api/carreras/${carreraSeleccionada.id_carrera}/`,
        {
          method: "PATCH",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ id_estado: 2 }), // 👈 ID del estado “Inactiva”
        }
      );

      if (response.ok) {
        const data = await response.json();
        alert(`Carrera marcada como ${data.nuevo_estado} ✅`);

        // 🔹 Obtener carrera actualizada desde el backend
        const refreshed = await fetch(
          `http://localhost:8000/api/carreras/${carreraSeleccionada.id_carrera}/`
        );
        const updatedCarrera = await refreshed.json();

        // 🔹 Actualizar datos visuales
        carreraSeleccionada = updatedCarrera;
        actualizarTablaDerecha(updatedCarrera);

        // 🔹 Actualizar solo la fila correspondiente (sin recargar toda la tabla)
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
        alert("Error al dar de baja la carrera.");
      }
    } catch (error) {
      console.error("Error al dar de baja:", error);
      alert("Error de conexión con el servidor.");
    }
  }

  // ----------------------------------------------------------
  // Guardar (crear o editar)
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
        alert(id ? "Carrera actualizada ✅" : "Carrera creada ✅");
        modal.style.display = "none";
        await cargarCarreras();
      } else {
        const err = await response.json();
        console.error(err);
        alert("Error al guardar la carrera");
      }
    } catch (error) {
      console.error("Error de red:", error);
      alert("No se pudo conectar con el servidor");
    } finally {
      isSubmitting = false;
    }
  });

  // ----------------------------------------------------------
  // Botones de acción (Alta, Baja, Modificación)
  // ----------------------------------------------------------
  buttons.forEach((btn) => {
    const text = btn.querySelector(".text").innerText.trim();
    if (text === "Alta") btn.addEventListener("click", abrirModalNueva);
    if (text === "Modificacion")
      btn.addEventListener("click", abrirModalEditar);
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
  // Inicialización
  // ----------------------------------------------------------
  cargarCarreras();
});
