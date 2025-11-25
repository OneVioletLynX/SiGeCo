document.addEventListener("DOMContentLoaded", () => {

  const modal = document.getElementById("altaModal");
  const form = document.getElementById("alumnoForm");
  const closeBtn = document.querySelector(".close");

  let isSubmitting = false;

  // ==========================================================
  //  FILTROS
  // ==========================================================
  let filtroEstado = "all";
  let filtroCarrera = "all";
  let filtroBusqueda = "";

  // -------------------------------------------------------------------
  //  VALIDACIONES DEL FORMULARIO DE ALUMNOS (errores debajo de cada input)
  // -------------------------------------------------------------------

  function limpiarErroresAlumno() {
    document.querySelectorAll(".error-msg").forEach(e => (e.innerText = ""));
  }

  function validarFormularioAlumno() {
    limpiarErroresAlumno();
    let valido = true;

    const form = document.getElementById("alumnoForm");

    const nombre = form.nombre;
    const apellido = form.apellido;
    const dni = form.dni;
    const email = form.email;
    const telefono = form.telefono;
    const fechaNac = form.fecha_nacimiento;

    // Helper para mostrar errores debajo del input
    const setError = (name, msg) => {
      const span = document.getElementById("error-" + name);
      if (span) span.innerText = msg;
      valido = false;
    };

    // --- Validaciones ---
    if (!nombre.value.trim()) {
      setError("nombre", "El nombre es obligatorio.");
    }

    if (!apellido.value.trim()) {
      setError("apellido", "El apellido es obligatorio.");
    }

    if (!/^[0-9]{7,8}$/.test(dni.value.trim())) {
      setError("dni", "Debe tener 7 u 8 números.");
    }

    if (email.value && !/^\S+@\S+\.\S+$/.test(email.value)) {
      setError("email", "Correo electrónico inválido.");
    }

    if (!/^[0-9]{6,}$/.test(telefono.value.trim())) {
      setError("telefono", "El teléfono debe tener al menos 6 números.");
    }

    if (!fechaNac.value) {
      setError("fecha_nacimiento", "La fecha es obligatoria.");
    } else {
      const hoy = new Date();
      const f = new Date(fechaNac.value);

      if (f > hoy) {
        setError("fecha_nacimiento", "No puede ser futura.");
      }

      const edad = hoy.getFullYear() - f.getFullYear();
      if (edad < 10) {
        setError("fecha_nacimiento", "Debe tener más de 10 años.");
      }
    }

    return valido;
  }

  // ======================================================================
  // MULTI-STEP PRO + VALIDACIÓN POR PASO
  // ======================================================================

  let currentStep = 0;
  const steps = document.querySelectorAll(".form-step");
  const stepIndicators = document.querySelectorAll(".step");
  const nextBtn = document.getElementById("nextBtn");
  const prevBtn = document.getElementById("prevBtn");
  const submitBtn = document.getElementById("submitBtn");
  const previewContainer = document.getElementById("previewDatos");

  function showStep(index) {
      steps.forEach((s, i) => {
          s.classList.toggle("active", i === index);
      });

      stepIndicators.forEach((step, i) => {
          step.classList.toggle("active", i <= index);
      });

      prevBtn.style.display = index === 0 ? "none" : "inline-block";
      nextBtn.style.display = index === steps.length - 1 ? "none" : "inline-block";
      submitBtn.style.display = index === steps.length - 1 ? "inline-block" : "none";

      currentStep = index;

      if (currentStep === steps.length - 1) {
          cargarVistaPrevia();
      }
  }

  prevBtn.addEventListener("click", () => {
      if (currentStep > 0) showStep(currentStep - 1);
  });

  nextBtn.addEventListener("click", () => {
      if (validarPasoActual()) {
          showStep(currentStep + 1);
      }
  });

  // =====================================================
  //  VALIDAR POR PASO
  // =====================================================
  function validarPasoActual() {
      limpiarErroresAlumno();

      const form = document.getElementById("alumnoForm");
      let valido = true;

      // Helper interno
      const setError = (name, msg) => {
          const span = document.getElementById("error-" + name);
          if (span) span.innerText = msg;
          valido = false;
      };

      // --------------------- PASO 1 ---------------------
      if (currentStep === 0) {
          if (!form.nombre.value.trim()) setError("nombre", "Ingrese un nombre.");
          if (!form.apellido.value.trim()) setError("apellido", "Ingrese un apellido.");

          if (!/^[0-9]{7,8}$/.test(form.dni.value.trim()))
              setError("dni", "Debe tener 7 u 8 números.");

          if (!form.fecha_nacimiento.value)
              setError("fecha_nacimiento", "Ingrese una fecha.");
      }

      // --------------------- PASO 2 ---------------------
      if (currentStep === 1) {
          if (!/^[0-9]{6,}$/.test(form.telefono.value.trim()))
              setError("telefono", "Teléfono inválido.");

          if (form.email.value && !/^\S+@\S+\.\S+$/.test(form.email.value))
              setError("email", "Correo inválido.");
      }

      // --------------------- PASO 3 ---------------------
      if (currentStep === 2) {
          if (!form.id_carrera.value)
              setError("id_carrera", "Seleccione una carrera.");

          if (!form.id_estado.value)
              setError("id_estado", "Seleccione un estado.");
      }

      return valido;
  }

  // =====================================================
  //  VISTA PREVIA FINAL (PASO 4)
  // =====================================================
  function cargarVistaPrevia() {
      const data = Object.fromEntries(new FormData(document.getElementById("alumnoForm")));

      let html = `
          <strong>Nombre:</strong> ${data.nombre}<br>
          <strong>Apellido:</strong> ${data.apellido}<br>
          <strong>DNI:</strong> ${data.dni}<br>
          <strong>Fecha nacimiento:</strong> ${data.fecha_nacimiento}<br><br>

          <strong>Dirección:</strong> ${data.direccion} ${data.numero}<br>
          <strong>Teléfono:</strong> (${data.prefijo}) ${data.telefono}<br>
          <strong>Email:</strong> ${data.email}<br><br>

          <strong>Carrera:</strong> ${document.querySelector("#id_carrera option:checked")?.textContent}<br>
          <strong>Estado:</strong> ${document.querySelector("#id_estado option:checked")?.textContent}<br>
          <strong>Año Ingreso:</strong> ${data.anio_ingreso}<br>
          <strong>Legajo:</strong> ${data.legajo}<br>
      `;

      previewContainer.innerHTML = html;
  }

  // =====================================================
  //  INICIALIZAR MULTISTEP AL ABRIR MODAL
  // =====================================================
  function resetMultiStep() {
      currentStep = 0;
      showStep(0);
  }

  // Integramos con abrir modal
  const originalBtnAlta = document.getElementById("btnAltaAlumno");
  originalBtnAlta.addEventListener("click", async () => {
      form.reset();
      delete form.dataset.editingId;

      await Promise.all([cargarCarrerasForm(), cargarEstadosForm()]);

      setReadOnlyMode(false);

      modal.style.display = "block";

      // 👇 ESTE ES EL FIX
      setTimeout(resetMultiStep, 0);
  });

  // Integramos con editar
  async function abrirModalEditar(id) {
      // tu función original sigue intacta
      // pero agregamos esto al final:
      resetMultiStep();
  }


  // ==========================================================
  //  MODO LECTURA / EDICIÓN
  // ==========================================================
  function setReadOnlyMode(enabled) {
    const inputs = form.querySelectorAll("input, select, textarea");
    inputs.forEach(el => {
      el.disabled = !!enabled;
      el.classList.toggle("readonly", enabled);
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

  // ==========================================================
  //  CHIPS (COLORES)
  // ==========================================================
  const PALETA = [
    { bg: "#E3F2FD", text: "#1565C0" }, // Azul
    { bg: "#E8F5E9", text: "#2E7D32" }, // Verde
    { bg: "#FFF3E0", text: "#EF6C00" }, // Naranja
    { bg: "#FCE4EC", text: "#C2185B" }, // Rosa
    { bg: "#F3E5F5", text: "#7B1FA2" }, // Púrpura
    { bg: "#E0F2F1", text: "#00796B" }, // Turquesa
    { bg: "#EDE7F6", text: "#5E35B1" }, // Violeta
    { bg: "#FFF8E1", text: "#FFA000" }, // Ámbar
    { bg: "#E0F7FA", text: "#00838F" }, // Cian
    { bg: "#F1F8E9", text: "#558B2F" }  // Verde limón
  ];

  function obtenerColorFijo(texto) {
    let hash = 0;
    for (let i = 0; i < texto.length; i++) {
      hash = texto.charCodeAt(i) + ((hash << 5) - hash);
    }
    return PALETA[Math.abs(hash) % PALETA.length];
  }

  const ESTADOS_PALETA = {
    "activo":   { bg: "#E8F5E9", text: "#2E7D32" },
    "inactivo": { bg: "#FFEBEE", text: "#C62828" },
    "baja":     { bg: "#FFF3E0", text: "#EF6C00" }
  };

  function formatearChipCarrera(carrera) {
    if (!carrera) return "-";
    const c = obtenerColorFijo(carrera);
    return `
      <span class="chip" style="background:${c.bg}; color:${c.text}">
        <span class="dot" style="background:${c.text}"></span>
        ${carrera}
      </span>
    `;
  }

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
  //  FUNCIONES REUTILIZABLES (VER / EDITAR / BAJA)
  // ==========================================================

  async function abrirModalEditar(id) {

    const response = await fetch(`http://localhost:8000/api/alumnos/${id}/`);
    const alumno = await response.json();

    await Promise.all([cargarCarrerasForm(), cargarEstadosForm()]);

    if (alumno.carrera_actual)
      document.getElementById("id_carrera").value = String(alumno.carrera_actual);

    if (alumno.estado_actual)
      document.getElementById("id_estado").value = String(alumno.estado_actual);

    for (const [key, value] of Object.entries(alumno)) {
      const input = form.querySelector(`[name="${key}"]`);
      if (input && key !== "id_carrera" && key !== "id_estado")
        input.value = value ?? "";
    }

    form.dataset.editingId = alumno.id_alumno;
    setReadOnlyMode(false);
    document.getElementById("modalTitle").innerText = "Modificar Alumno";
    modal.style.display = "block";
  }

  async function darDeBajaAlumno(id) {
    if (!id) return;

    try {
      const response = await fetch(`http://localhost:8000/api/alumnos/${id}/`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ id_estado: 2 })
      });

      if (response.ok) {
        console.log("Alumno dado de baja correctamente");
        await cargarAlumnos();
      } else {
        const errTxt = await response.text();
        console.error("Error al dar de baja el alumno:", errTxt);
      }

    } catch (error) {
      console.error("Error de conexión con el backend al dar de baja:", error);
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
    if (filtroBusqueda)       url += `search=${encodeURIComponent(filtroBusqueda)}&`;

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
        <td>${formatearChipCarrera(alumno.carrera_nombre)}</td>
        <td>${formatearChipEstado(alumno.estado_nombre)}</td>
        <td>
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
      if (label === "prev") li.classList.add("ulpgcds-pager__item--prev");
      if (label === "next") li.classList.add("ulpgcds-pager__item--next");

      const btn = document.createElement("a");
      btn.href = "#";
      btn.classList.add("pagination__link");

      if (label === "prev") {
        btn.innerHTML = `<img src="/static/shared/assets/arrow_left.svg" class="pager-icon">`;
      } 
      else if (label === "next") {
        btn.innerHTML = `<img src="/static/shared/assets/arrow_right.svg" class="pager-icon">`;
      }
      else {
        btn.textContent = label;
      }

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

    addBtn("prev", paginaActual - 1, paginaActual === 1);

    for (let i = 1; i <= total; i++) {
      addBtn(i, i, false, paginaActual === i);
    }

    addBtn("next", paginaActual + 1, paginaActual === total);
  }

  // ==========================================================
  //  BOTONES DE CADA FILA (EDITAR / BAJA)
  // ==========================================================
  document.addEventListener("click", async e => {

    const btn = e.target.closest("button");

    if (!btn) return;

    const id = btn.dataset.id;

    if (btn.classList.contains("btn-editar")) {
      abrirModalEditar(id);
    }

    if (btn.classList.contains("btn-baja")) {
      darDeBajaAlumno(id);
    }
  });

  
  // ==========================================================
  //  BOTÓN ALTA (Nuevo Alumno)
  // ==========================================================
  document.getElementById("btnAltaAlumno").addEventListener("click", async () => {
    form.reset();
    delete form.dataset.editingId;

    setReadOnlyMode(false);

    await Promise.all([cargarCarrerasForm(), cargarEstadosForm()]);

    document.getElementById("modalTitle").innerText = "Nuevo Alumno";

    modal.style.display = "block";
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

  let searchTimeout = null;
  document.getElementById("buscadorAlumno").addEventListener("input", e => {
    clearTimeout(searchTimeout);
    filtroBusqueda = e.target.value.trim();

    searchTimeout = setTimeout(() => cargarAlumnos(), 300);
  });

  // ==========================================================
  //  CARGAR SELECTS (FORMULARIO Y FILTROS)
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
  //  FORMULARIO (ALTA / MODIFICAR)
  // ==========================================================
  form.addEventListener("submit", async e => {
    e.preventDefault();
    if (isSubmitting) return;
    isSubmitting = true;

    // Validaciones front
    const esValido = validarFormularioAlumno();

    // Validar selects Carrera / Estado sin alerts
    const data = Object.fromEntries(new FormData(form));
    let selectsValidos = true;

    if (!data.id_carrera) {
      const spanCarrera = document.getElementById("error-id_carrera");
      if (spanCarrera) spanCarrera.innerText = "Seleccione una carrera.";
      selectsValidos = false;
    }
    if (!data.id_estado) {
      const spanEstado = document.getElementById("error-id_estado");
      if (spanEstado) spanEstado.innerText = "Seleccione un estado.";
      selectsValidos = false;
    }

    if (!esValido || !selectsValidos) {
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
        body: JSON.stringify(data)
      });

      if (response.ok) {
        form.reset();
        delete form.dataset.editingId;
        modal.style.display = "none";
        await cargarAlumnos();
        console.log(id ? "Alumno actualizado" : "Alumno creado");
      } else {
        const err = await response.json().catch(() => null);
        console.error("Error al guardar:", err || "(sin detalle JSON)");
        // Si quisieras, acá podrías mapear errores del backend a los spans
      }

    } catch (error) {
      console.error("Error de conexión con el backend:", error);
    } finally {
      isSubmitting = false;
    }
  });

  // ==========================================================
  //  MODAL
  // ==========================================================
  closeBtn.onclick = () => (modal.style.display = "none");
  window.onclick = e => {
    if (e.target === modal) modal.style.display = "none";
  };

  // ==========================================================
  //  INICIO
  // ==========================================================
  (async () => {
    await Promise.all([cargarCarreras(), cargarEstados()]);
    await cargarAlumnos();
  })();

});
