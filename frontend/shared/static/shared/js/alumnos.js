document.addEventListener("DOMContentLoaded", () => {
  const modal = document.getElementById("altaModal");
  const form = document.getElementById("alumnoForm");
  const closeBtn = document.querySelector(".close");
  const tabla = document.querySelector("#tabla-alumnos tbody");

  let alumnoSeleccionado = null;
  let isSubmitting = false;

  // 🔹 Filtros
  let filtroEstado = "1";
  let filtroCarrera = "all";
  let filtroBusqueda = "";

  // ----------------------------------------------------------
  // 🔹 Función: Modo lectura
  // ----------------------------------------------------------
  function setReadOnlyMode(enabled) {
    const inputs = form.querySelectorAll("input, select, textarea");
    inputs.forEach(el => {
      el.disabled = !!enabled;
      if (enabled) el.classList.add("readonly");
      else el.classList.remove("readonly");
    });

    const submitBtn = document.getElementById("submitBtn");
    if (submitBtn) submitBtn.style.display = enabled ? "none" : "inline-block";

    const title = document.getElementById("modalTitle");
    if (title)
      title.innerText = enabled
        ? "Ver Alumno"
        : form.dataset.editingId
          ? "Modificar Alumno"
          : "Nuevo Alumno";
  }

  // ----------------------------------------------------------
  // 🔹 Cargar alumnos
  // ----------------------------------------------------------
  async function cargarAlumnos() {
    let url = "http://localhost:8000/api/alumnos/?";

    if (filtroEstado && filtroEstado !== "all") url += `estado=${filtroEstado}&`;
    if (filtroCarrera && filtroCarrera !== "all") url += `carrera=${filtroCarrera}&`;
    if (filtroBusqueda) url += `search=${encodeURIComponent(filtroBusqueda)}&`;

    const response = await fetch(url);
    const alumnos = await response.json();
    tabla.innerHTML = "";

    alumnos.forEach(alumno => {
      const tr = document.createElement("tr");
      tr.dataset.id = alumno.id_alumno;
      tr.innerHTML = `
        <td>${alumno.apellido}, ${alumno.nombre}</td>
        <td>${alumno.dni}</td>
        <td>${alumno.ciudad || "-"}</td>
        <td>${alumno.direccion || "-"}</td>
        <td>${alumno.telefono || "-"}</td>
        <td>${alumno.email}</td>
      `;
      tabla.appendChild(tr);
    });
  }

  // ----------------------------------------------------------
  // 🔹 Cargar listas
  // ----------------------------------------------------------
  async function cargarCarreras() {
    const selectCarrera = document.getElementById("filtroCarrera");
    const response = await fetch("http://localhost:8000/api/carreras/");
    const carreras = await response.json();

    carreras.forEach(c => {
      const opt = document.createElement("option");
      opt.value = c.id_carrera;
      opt.textContent = c.descripcion;
      selectCarrera.appendChild(opt);
    });
  }

  async function cargarEstados() {
    const selectEstado = document.getElementById("filtroEstado");
    selectEstado.innerHTML = `<option value="all" selected>Todos</option>`;

    const response = await fetch("http://localhost:8000/api/estados/");
    const estados = await response.json();

    estados.forEach(e => {
      const opt = document.createElement("option");
      opt.value = e.id_estado;
      opt.textContent = e.descripcion;
      selectEstado.appendChild(opt);
    });
  }


  async function cargarCarrerasForm() {
    const select = document.getElementById("id_carrera");
    if (!select) return;
    select.innerHTML = `<option value="" disabled selected>Todas</option>`;
    const response = await fetch("http://localhost:8000/api/carreras/");
    const carreras = await response.json();
    carreras.forEach(c => {
      const opt = document.createElement("option");
      opt.value = c.id_carrera;
      opt.textContent = c.descripcion;
      select.appendChild(opt);
    });
  }

  async function cargarEstadosForm() {
    const select = document.getElementById("id_estado");
    if (!select) return;
    select.innerHTML = `<option value="" disabled selected>Seleccione un estado</option>`;
    const response = await fetch("http://localhost:8000/api/estados/");
    const estados = await response.json();
    estados.forEach(e => {
      const opt = document.createElement("option");
      opt.value = e.id_estado;
      opt.textContent = e.descripcion;
      select.appendChild(opt);
    });
  }

  // ----------------------------------------------------------
  // 🔹 Filtros y buscador
  // ----------------------------------------------------------
  document.getElementById("filtroEstado").addEventListener("change", async e => {
    filtroEstado = e.target.value;
    await cargarAlumnos();
  });

  document.getElementById("filtroCarrera").addEventListener("change", async e => {
    filtroCarrera = e.target.value;
    await cargarAlumnos();
  });

// 🔹 Buscador con debounce (espera 300ms después de dejar de tipear)
  let searchTimeout = null;

  document.getElementById("buscadorAlumno").addEventListener("input", e => {
    clearTimeout(searchTimeout);
    filtroBusqueda = e.target.value.trim();

    searchTimeout = setTimeout(() => {
      cargarAlumnos();
    }, 300); // 300 ms de espera
  });


  // ----------------------------------------------------------
  // 🔹 Selección de fila
  // ----------------------------------------------------------
  document.addEventListener("click", e => {
    const fila = e.target.closest("#tabla-alumnos tbody tr");
    if (!fila) return;
    document.querySelectorAll("#tabla-alumnos tbody tr").forEach(tr => tr.classList.remove("selected"));
    fila.classList.add("selected");
    alumnoSeleccionado = fila.dataset.id;
  });

  // ----------------------------------------------------------
  // 🔹 Botones de acción
  // ----------------------------------------------------------
  document.querySelectorAll(".action-button").forEach(btn => {
    const text = btn.querySelector(".text").innerText.trim();

    // Alta
    if (text === "Alta") {
      btn.addEventListener("click", async () => {
        form.reset();
        delete form.dataset.editingId;
        setReadOnlyMode(false);
        await Promise.all([cargarCarrerasForm(), cargarEstadosForm()]);
        const title = document.getElementById("modalTitle");
        if (title) title.innerText = "Nuevo Alumno";
        modal.style.display = "block";
      });
    }

    // Modificación
    if (text === "Modificacion") {
      btn.addEventListener("click", async () => {
        if (!alumnoSeleccionado) {
          alert("Seleccioná primero un alumno.");
          return;
        }

        // Traer datos del alumno
        const response = await fetch(`http://localhost:8000/api/alumnos/${alumnoSeleccionado}/`);
        const alumno = await response.json();

        // Cargar selects y esperar
        await Promise.all([cargarCarrerasForm(), cargarEstadosForm()]);

        // Preseleccionar carrera y estado (vienen del backend)
        if (alumno.carrera_actual) {
          const selCarrera = document.getElementById("id_carrera");
          if (selCarrera) selCarrera.value = String(alumno.carrera_actual);
        }
        if (alumno.estado_actual) {
          const selEstado = document.getElementById("id_estado");
          if (selEstado) selEstado.value = String(alumno.estado_actual);
        }

        // Rellenar los demás campos
        for (const [key, value] of Object.entries(alumno)) {
          const input = form.querySelector(`[name="${key}"]`);
          if (input && key !== "id_carrera" && key !== "id_estado") input.value = value ?? "";
        }

        form.dataset.editingId = alumno.id_alumno;
        setReadOnlyMode(false);
        document.getElementById("modalTitle").innerText = "Modificar Alumno";
        modal.style.display = "block";
      });
    }

    // Ver
    if (text === "Ver") {
      btn.addEventListener("click", async () => {
        if (!alumnoSeleccionado) {
          alert("Seleccioná primero un alumno.");
          return;
        }

        const response = await fetch(`http://localhost:8000/api/alumnos/${alumnoSeleccionado}/`);
        const alumno = await response.json();

        await Promise.all([cargarCarrerasForm(), cargarEstadosForm()]);

        if (alumno.carrera_actual) document.getElementById("id_carrera").value = String(alumno.carrera_actual);
        if (alumno.estado_actual) document.getElementById("id_estado").value = String(alumno.estado_actual);

        for (const [key, value] of Object.entries(alumno)) {
          const input = form.querySelector(`[name="${key}"]`);
          if (input && key !== "id_carrera" && key !== "id_estado") input.value = value ?? "";
        }

        delete form.dataset.editingId;
        setReadOnlyMode(true);
        modal.style.display = "block";
      });
    }

    // Baja
    if (text === "Baja") {
      btn.addEventListener("click", async () => {
        if (!alumnoSeleccionado) {
          alert("Seleccioná primero un alumno.");
          return;
        }

        if (!confirm("¿Deseás dar de baja al alumno seleccionado?")) return;

        try {
          const response = await fetch(`http://localhost:8000/api/alumnos/${alumnoSeleccionado}/`, {
            method: "PATCH",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ id_estado: 2 }),
          });

          if (response.ok) {
            alert("Alumno dado de baja correctamente ✅");
            await cargarAlumnos();
          } else {
            alert("Error al dar de baja el alumno.");
          }
        } catch (error) {
          console.error(error);
          alert("Error de conexión con el backend.");
        }
      });
    }
  });

  // ----------------------------------------------------------
  // 🔹 Enviar formulario
  // ----------------------------------------------------------
  form.addEventListener("submit", async e => {
    e.preventDefault();
    if (isSubmitting) return;
    isSubmitting = true;

    const data = Object.fromEntries(new FormData(form));

    if (!data.id_carrera) {
      alert("Debes seleccionar una carrera antes de guardar el alumno.");
      isSubmitting = false;
      return;
    }

    const id = form.dataset.editingId;
    const method = id ? "PUT" : "POST";
    const url = id
      ? `http://localhost:8000/api/alumnos/${id}/`
      : `http://localhost:8000/api/alumnos/`;

    try {
      console.log("Datos enviados:", data);

      const response = await fetch(url, {
        method,
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data),
      });

      if (response.ok) {
        alert(id ? "Alumno actualizado ✅" : "Alumno creado ✅");
        form.reset();
        delete form.dataset.editingId;
        modal.style.display = "none";
        await cargarAlumnos();
      } else {
        const err = await response.json();
        alert("Error al guardar: " + JSON.stringify(err));
      }
    } catch (error) {
      console.error("Error:", error);
      alert("Error de conexión con el backend");
    } finally {
      isSubmitting = false;
    }
  });

  // ----------------------------------------------------------
  // 🔹 Cerrar modal
  // ----------------------------------------------------------
  closeBtn.onclick = () => (modal.style.display = "none");
  window.onclick = e => {
    if (e.target === modal) modal.style.display = "none";
  };

  // ----------------------------------------------------------
  // 🔹 Inicialización
  // ----------------------------------------------------------
  (async () => {
    await Promise.all([cargarCarreras(), cargarEstados()]);
    await cargarAlumnos();
  })();
});
