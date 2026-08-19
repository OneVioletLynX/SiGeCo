// Auth global desde auth.js (cargado en base.html)

document.addEventListener("DOMContentLoaded", () => {

  if (!getToken()) { logout(); return; }

  const API     = "http://127.0.0.1:8000/api";
  const seccion = document.getElementById("seccionFormCarrera");
  const form    = document.getElementById("formCarrera");
  const title   = document.getElementById("formCarreraTitle");
  const tabla   = document.getElementById("tabla-carreras");

  let isSubmitting     = false;
  let todasLasCarreras = [];

  // ===========================
  // COLOR PICKER
  // ===========================
  function aclararColor(hex, porcentaje) {
    const num = parseInt(hex.replace("#", ""), 16);
    let r = (num >> 16) + porcentaje;
    let g = ((num >> 8) & 0x00ff) + porcentaje;
    let b = (num & 0x0000ff) + porcentaje;
    r = r > 255 ? 255 : r; g = g > 255 ? 255 : g; b = b > 255 ? 255 : b;
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
    if (!colorPicker) return;
    colorPicker.innerHTML = "";
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
        if (hiddenColorInput) hiddenColorInput.value = color;
        actualizarPreview();
      });
      colorPicker.appendChild(div);
    });
  }

  function actualizarPreview() {
    const chip = document.querySelector(".chip-demo");
    if (!chip) return;
    const fondoClaro = aclararColor(colorSeleccionado, 150);
    chip.style.backgroundColor = fondoClaro;
    chip.style.color           = colorSeleccionado;
    chip.innerHTML = `
      <span class="dot" style="background:${colorSeleccionado}"></span>
      ${nombreInput?.value || "Nombre"}
    `;
  }

  // No ejecutar en carga — sólo al abrir el form
  nombreInput?.addEventListener("input", actualizarPreview);

  // ===========================
  // VALIDACIÓN
  // ===========================
  function setError(inputId, message) {
    const el = document.getElementById(inputId);
    if (el) el.classList.add("has-error");
    const err = document.getElementById("error-" + inputId);
    if (err) err.textContent = message;
  }

  function clearError(inputId) {
    const el = document.getElementById(inputId);
    if (el) el.classList.remove("has-error");
    const err = document.getElementById("error-" + inputId);
    if (err) err.textContent = "";
  }

  function clearAllErrors() {
    ["descripcion", "inscripcion", "cuota"].forEach(clearError);
  }

  // Blur validation
  nombreInput.addEventListener("blur", () => {
    const v = nombreInput.value.trim();
    if (!v) setError("descripcion", "Campo requerido");
    else if (v.length < 3) setError("descripcion", "Debe tener al menos 3 caracteres");
    else clearError("descripcion");
  });

  document.getElementById("inscripcion")?.addEventListener("blur", e => {
    const v = parseFloat(e.target.value);
    if (!e.target.value || isNaN(v) || v <= 0) setError("inscripcion", "Debe ser mayor a 0");
    else clearError("inscripcion");
  });

  document.getElementById("cuota")?.addEventListener("blur", e => {
    const v = parseFloat(e.target.value);
    if (!e.target.value || isNaN(v) || v <= 0) setError("cuota", "Debe ser mayor a 0");
    else clearError("cuota");
  });

  // ===========================
  // FORMATO VISUAL
  // ===========================
  function formatearChipEstado(estado) {
    if (!estado) return "-";
    const estadoLower = estado.toLowerCase();
    return `<span class="chip chip-${estadoLower}">
      <span class="dot"></span>${estado}
    </span>`;
  }

  function formatearMoneda(valor) {
    if (valor === null || valor === undefined) return "—";
    return `$${Number(valor).toLocaleString("es-AR")}`;
  }

  // ===========================
  // RENDER TABLA
  // ===========================
  function renderTabla(carreras) {
    tabla.innerHTML = "";

    if (!carreras.length) {
      tabla.innerHTML = `
        <tr>
          <td colspan="5" style="text-align:center;padding:3rem;color:var(--text-muted);">
            <span class="material-icons" style="font-size:2.5rem;display:block;margin-bottom:0.5rem;opacity:0.4;">school</span>
            Sin carreras para mostrar.
          </td>
        </tr>`;
      return;
    }

    carreras.forEach(carrera => {
      const esActivo = (carrera.estado_actual || "").toLowerCase() === "activo";
      const tr = document.createElement("tr");
      tr.innerHTML = `
        <td>${carrera.descripcion}</td>
        <td>${formatearChipEstado(carrera.estado_actual)}</td>
        <td>${formatearMoneda(carrera.cuota_vigente)}</td>
        <td>${formatearMoneda(carrera.inscripcion_vigente)}</td>
        <td class="acciones-col">
          <div style="position:relative; display:inline-block;">
            <button class="btn-menu-carrera" data-id="${carrera.id_carrera}"
              style="background:none; border:none; cursor:pointer; padding:0.3rem 0.6rem;
                     border-radius:6px; color:#6b7280; font-size:1.4rem; line-height:1;
                     transition:background 0.15s;"
              onmouseenter="this.style.background='#f3f4f6'"
              onmouseleave="this.style.background='none'">
              ⋮
            </button>
            <div class="dropdown-menu-carrera hidden" data-id="${carrera.id_carrera}">
              <button class="menu-item-carrera btn-editar-carrera" data-id="${carrera.id_carrera}">
                <span class="material-icons" style="font-size:18px; color:#6b7280;">edit</span>
                Editar
              </button>
              <button class="menu-item-carrera btn-historial-carrera" data-id="${carrera.id_carrera}" data-nombre="${carrera.descripcion}">
                <span class="material-icons" style="font-size:18px; color:#6b7280;">history</span>
                Ver historial
              </button>
              <div style="border-top:1px solid #e5e7eb; margin:4px 0;"></div>
              <button class="menu-item-carrera btn-cambiar-estado-carrera danger"
                data-id="${carrera.id_carrera}" data-estado="${carrera.estado_actual}">
                <span class="material-icons" style="font-size:18px;">${esActivo ? 'block' : 'check_circle'}</span>
                ${esActivo ? 'Dar de baja' : 'Reactivar'}
              </button>
            </div>
          </div>
        </td>
      `;
      tabla.appendChild(tr);
    });
  }

  // ===========================
  // CARGAR CARRERAS
  // ===========================
  async function cargarCarreras() {
    tabla.innerHTML = `
      <tr>
        <td colspan="5" style="text-align:center;padding:2rem;color:var(--text-muted);">
          Cargando...
        </td>
      </tr>`;

    try {
      const response = await authFetch(`${API}/carreras/`);
      if (!response) return;
      let carreras = await response.json();
      todasLasCarreras = carreras.results || carreras;
      filtrarYRender();
    } catch (error) {
      console.error("Error cargando carreras:", error);
      tabla.innerHTML = `<tr><td colspan="5" style="text-align:center;padding:2rem;color:#dc2626;">Error al cargar las carreras.</td></tr>`;
    }
  }

  // ===========================
  // BÚSQUEDA
  // ===========================
  function filtrarYRender() {
    const q = (document.getElementById("buscadorCarrera")?.value || "").toLowerCase().trim();
    const filtradas = q
      ? todasLasCarreras.filter(c => c.descripcion.toLowerCase().includes(q))
      : todasLasCarreras;
    renderTabla(filtradas);
  }

  document.getElementById("buscadorCarrera")?.addEventListener("input", filtrarYRender);

  // ===========================
  // MENÚ ⋮ — abrir/cerrar
  // ===========================
  document.addEventListener("click", e => {
    if (!e.target.closest(".btn-menu-carrera") && !e.target.closest(".dropdown-menu-carrera")) {
      document.querySelectorAll(".dropdown-menu-carrera").forEach(m => m.classList.add("hidden"));
    }
  });

  document.addEventListener("click", e => {
    const btn = e.target.closest(".btn-menu-carrera");
    if (!btn) return;
    e.stopPropagation();

    const id       = btn.dataset.id;
    const dropdown = document.querySelector(`.dropdown-menu-carrera[data-id="${id}"]`);

    document.querySelectorAll(".dropdown-menu-carrera").forEach(m => {
      if (m !== dropdown) m.classList.add("hidden");
    });

    if (dropdown.classList.contains("hidden")) {
      const rect = btn.getBoundingClientRect();
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

  // Editar
  document.addEventListener("click", e => {
    const btn = e.target.closest(".btn-editar-carrera");
    if (!btn) return;
    document.querySelectorAll(".dropdown-menu-carrera").forEach(m => m.classList.add("hidden"));
    abrirFormEditar(btn.dataset.id);
  });

  // Cambiar estado
  let _bajaCarreraId    = null;
  let _bajaCarreraActual = null;

  const modalBaja          = document.getElementById("modalBajaCarrera");
  const checkInactivar     = document.getElementById("checkInactivarAlumnos");
  const btnConfirmarBaja   = document.getElementById("btnConfirmarBaja");

  function cerrarModalBaja() {
    modalBaja.classList.add("hidden");
    checkInactivar.checked = false;
    _bajaCarreraId     = null;
    _bajaCarreraActual = null;
  }

  document.getElementById("btnCerrarBaja")?.addEventListener("click", cerrarModalBaja);
  document.getElementById("btnCancelarBaja")?.addEventListener("click", cerrarModalBaja);
  modalBaja?.addEventListener("click", e => { if (e.target === modalBaja) cerrarModalBaja(); });

  document.addEventListener("click", e => {
    const btn = e.target.closest(".btn-cambiar-estado-carrera");
    if (!btn) return;
    document.querySelectorAll(".dropdown-menu-carrera").forEach(m => m.classList.add("hidden"));

    const estadoActual = btn.dataset.estado;
    const esActivo     = (estadoActual || "").toLowerCase() === "activo";

    if (esActivo) {
      // Dar de baja → abrir modal custom con checkbox
      const bajaId = btn.dataset.id;
      if (!bajaId || bajaId === "null" || isNaN(bajaId)) return;
      _bajaCarreraId     = bajaId;
      _bajaCarreraActual = estadoActual;
      modalBaja.classList.remove("hidden");
    } else {
      // Reactivar → confirmación simple
      const reactivarId = btn.dataset.id;
      if (!reactivarId || reactivarId === "null") return;
      showConfirm("¿Querés reactivar esta carrera?", "Confirmar").then(async ok => {
        if (!ok) return;
        try {
          const resp = await authFetch(`${API}/carreras/${reactivarId}/`, {
            method : "PATCH",
            headers: { "Content-Type": "application/json" },
            body   : JSON.stringify({ id_estado: 1 }),
          });
          if (resp && resp.ok) {
            showAlert("Carrera reactivada correctamente.", "success");
            await cargarCarreras();
          } else {
            showAlert("No se pudo reactivar la carrera.", "error");
          }
        } catch {
          showAlert("Error de conexión.", "error");
        }
      });
    }
  });

  btnConfirmarBaja?.addEventListener("click", async () => {
    if (!_bajaCarreraId || _bajaCarreraId === "null" || isNaN(_bajaCarreraId)) return;
    const idParaBaja       = _bajaCarreraId;   // capturar antes de que cerrarModalBaja lo resetee
    const inactivarAlumnos = checkInactivar.checked;
    cerrarModalBaja();

    try {
      const resp = await authFetch(`${API}/carreras/${idParaBaja}/`, {
        method:  "PATCH",
        headers: { "Content-Type": "application/json" },
        body:    JSON.stringify({ id_estado: 2, inactivar_alumnos: inactivarAlumnos }),
      });
      if (resp && resp.ok) {
        const msg = inactivarAlumnos
          ? "Carrera dada de baja y alumnos activos inactivados."
          : "Carrera dada de baja correctamente.";
        showAlert(msg, "success");
        await cargarCarreras();
      } else {
        showAlert("No se pudo dar de baja la carrera.", "error");
      }
    } catch {
      showAlert("Error de conexión.", "error");
    }
  });

  // ===========================
  // FORM — abrir nueva
  // ===========================
  function mostrarFormSoloForm() {
    document.getElementById("barraBusqueda")?.style.setProperty("display", "none");
    document.getElementById("sortableTable")?.style.setProperty("display", "none");
    seccion.style.display = "block";
    window.scrollTo({ top: 0, behavior: "smooth" });
  }

  function abrirFormNueva() {
    if (!form || !seccion) return;
    form.reset();
    clearAllErrors();
    if (document.getElementById("carreraId")) document.getElementById("carreraId").value = "";
    if (title) title.innerText = "Nueva Carrera";

    colorSeleccionado = COLORES_CARRERA[0];
    if (hiddenColorInput) hiddenColorInput.value = colorSeleccionado;
    renderColorPicker();
    actualizarPreview();
    mostrarFormSoloForm();
    setTimeout(() => nombreInput?.focus(), 100);
  }

  // ===========================
  // FORM — abrir editar
  // ===========================
  async function abrirFormEditar(id) {
    try {
      const response = await authFetch(`${API}/carreras/${id}/`);
      if (!response) return;
      const carrera = await response.json();

      if (!form || !seccion) return;
      form.reset();
      clearAllErrors();
      const elId  = document.getElementById("carreraId");
      const elDes = document.getElementById("descripcion");
      const elIns = document.getElementById("inscripcion");
      const elCuo = document.getElementById("cuota");
      if (elId)  elId.value  = carrera.id_carrera;
      if (elDes) elDes.value = carrera.descripcion;
      if (elIns) elIns.value = carrera.inscripcion_vigente ?? "";
      if (elCuo) elCuo.value = carrera.cuota_vigente ?? "";

      colorSeleccionado = carrera.color || COLORES_CARRERA[0];
      if (hiddenColorInput) hiddenColorInput.value = colorSeleccionado;
      renderColorPicker();
      actualizarPreview();
      if (title) title.innerText = "Modificar Carrera";
      mostrarFormSoloForm();
      setTimeout(() => nombreInput?.focus(), 100);

    } catch (error) {
      console.error("Error al obtener carrera:", error);
      showAlert("No se pudo cargar la carrera.", "error");
    }
  }

  function cerrarForm() {
    seccion.style.display = "none";
    document.getElementById("barraBusqueda")?.style.removeProperty("display");
    document.getElementById("sortableTable")?.style.removeProperty("display");
    form.reset();
    clearAllErrors();
    isSubmitting = false;
  }

  // ===========================
  // FORM — abrir/cerrar (botones, Escape)
  // ===========================
  document.getElementById("btnNuevaCarrera")?.addEventListener("click", abrirFormNueva);
  document.getElementById("btnCancelarForm")?.addEventListener("click", cerrarForm);

  document.addEventListener("keydown", e => {
    if (e.key === "Escape" && seccion.style.display !== "none") cerrarForm();
  });

  // ===========================
  // GUARDAR (POST / PUT)
  // ===========================
  form.addEventListener("submit", async e => {
    e.preventDefault();
    if (isSubmitting) return;

    clearAllErrors();
    let hayErrores = false;

    const descripcion = document.getElementById("descripcion").value.trim();
    const inscripcion = document.getElementById("inscripcion").value;
    const cuota       = document.getElementById("cuota").value;

    if (descripcion.length < 3)                       { setError("descripcion", "Debe tener al menos 3 caracteres"); hayErrores = true; }
    if (!inscripcion || parseFloat(inscripcion) <= 0) { setError("inscripcion", "Debe ser mayor a 0");               hayErrores = true; }
    if (!cuota       || parseFloat(cuota) <= 0)       { setError("cuota",       "Debe ser mayor a 0");               hayErrores = true; }

    if (hayErrores) return;

    isSubmitting = true;
    const btnGuardar = form.querySelector(".btn-guardar-modal");
    const textoOriginal = btnGuardar?.textContent || "Guardar";
    if (btnGuardar) { btnGuardar.textContent = "Guardando..."; btnGuardar.disabled = true; }

    const idRaw = document.getElementById("carreraId").value;
    const id    = idRaw && idRaw !== "null" && !isNaN(idRaw) ? idRaw : null;
    const data = {
      descripcion,
      inscripcion: parseFloat(inscripcion),
      cuota:       parseFloat(cuota),
      color:       hiddenColorInput.value,
    };
    const method = id ? "PUT"  : "POST";
    const url    = id ? `${API}/carreras/${id}/` : `${API}/carreras/`;

    try {
      const response = await authFetch(url, {
        method,
        headers: { "Content-Type": "application/json" },
        body:    JSON.stringify(data),
      });

      if (response && response.ok) {
        showAlert(id ? "Carrera actualizada correctamente." : "Carrera creada correctamente.", "success");
        cerrarForm();
        await cargarCarreras();
      } else {
        // Mostrar errores del servidor
        let mensajeError = "Error al guardar la carrera.";
        try {
          const errData = await response.json();
          const msgs = [];
          for (const [campo, errores] of Object.entries(errData)) {
            const lista = Array.isArray(errores) ? errores : [errores];
            if (["descripcion", "inscripcion", "cuota"].includes(campo)) {
              setError(campo, lista[0]);
            } else {
              msgs.push(lista.join(", "));
            }
          }
          if (msgs.length) mensajeError = msgs.join(" | ");
          else if (!["descripcion", "inscripcion", "cuota"].some(c => errData[c])) {
            mensajeError = "Error al guardar la carrera.";
          } else {
            mensajeError = null;
          }
        } catch { /* no JSON */ }
        if (mensajeError) showAlert(mensajeError, "error");
      }
    } catch {
      showAlert("No se pudo conectar con el servidor.", "error");
    } finally {
      isSubmitting = false;
      if (btnGuardar) { btnGuardar.textContent = textoOriginal; btnGuardar.disabled = false; }
    }
  });

  // ===========================
  // HISTORIAL DE VALORES
  // ===========================
  const modalHistorial   = document.getElementById("modalHistorial");
  const historialContent = document.getElementById("historialContent");
  const historialTitulo  = document.getElementById("historialTitulo");

  function cerrarHistorial() {
    modalHistorial.classList.add("hidden");
  }

  document.getElementById("btnCerrarHistorial")?.addEventListener("click", cerrarHistorial);
  modalHistorial?.addEventListener("click", e => {
    if (e.target === modalHistorial) cerrarHistorial();
  });
  document.addEventListener("keydown", e => {
    if (e.key === "Escape" && !modalHistorial.classList.contains("hidden")) cerrarHistorial();
  });

  document.addEventListener("click", async e => {
    const btn = e.target.closest(".btn-historial-carrera");
    if (!btn) return;
    document.querySelectorAll(".dropdown-menu-carrera").forEach(m => m.classList.add("hidden"));

    const id     = btn.dataset.id;
    const nombre = btn.dataset.nombre;
    historialTitulo.textContent = `Historial de valores — ${nombre}`;
    historialContent.innerHTML  = `<p class="historial-empty">Cargando...</p>`;
    modalHistorial.classList.remove("hidden");

    try {
      const resp = await authFetch(`${API}/valores/?id_carrera=${id}`);
      if (!resp || !resp.ok) throw new Error();
      const valores = await resp.json();

      if (!valores.length) {
        historialContent.innerHTML = `<p class="historial-empty">Sin registros de valores para esta carrera.</p>`;
        return;
      }

      // Agrupar por concepto dinámicamente
      const grupos = {};
      valores.forEach(v => {
        const key = v.id_concepto_nombre || `Concepto ${v.id_concepto}`;
        if (!grupos[key]) grupos[key] = [];
        grupos[key].push(v);
      });

      function renderSeccion(titulo, registros) {
        const rows = registros.map((v, i) => {
          const fecha   = new Date(v.fecha_inicio + "T00:00:00").toLocaleDateString("es-AR", { day:"2-digit", month:"2-digit", year:"numeric" });
          const badge   = i === 0 ? `<span class="historial-vigente-badge">Vigente</span>` : "";
          const importe = `$${Number(v.importe).toLocaleString("es-AR", { minimumFractionDigits: 2 })}`;
          return `<tr>
            <td>${fecha}${badge}</td>
            <td style="font-weight:${i===0?'600':'400'}">${importe}</td>
          </tr>`;
        }).join("");
        return `
          <p class="historial-section-title">${titulo}</p>
          <table class="historial-table">
            <thead><tr><th>Fecha de vigencia</th><th>Importe</th></tr></thead>
            <tbody>${rows}</tbody>
          </table>`;
      }

      historialContent.innerHTML = Object.entries(grupos)
        .map(([nombre, registros]) => renderSeccion(nombre, registros))
        .join("");

    } catch {
      historialContent.innerHTML = `<p class="historial-empty">No se pudo cargar el historial.</p>`;
    }
  });

  // ===========================
  // INICIO
  // ===========================
  cargarCarreras();
});
