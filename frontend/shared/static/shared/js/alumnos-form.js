// ===========================
// AUTH
// ===========================
function getToken() {
  return localStorage.getItem("sigeco_access") || "";
}

function logout() {
  localStorage.removeItem("sigeco_access");
  localStorage.removeItem("sigeco_refresh");
  localStorage.removeItem("sigeco_rol");
  localStorage.removeItem("sigeco_nombre");
  localStorage.removeItem("sigeco_permisos");
  document.cookie = "sigeco_access=; path=/; max-age=0";
  window.location.href = "http://127.0.0.1:8001/";
}

async function authFetch(url, options = {}) {
  const token = getToken();
  if (!token) { logout(); return; }
  const headers = { ...(options.headers || {}), "Authorization": `Bearer ${token}` };
  const resp = await fetch(url, { ...options, headers });
  if (resp.status === 401) { logout(); return; }
  return resp;
}

document.addEventListener("DOMContentLoaded", async () => {

  if (!getToken()) { logout(); return; }

  const API               = "http://127.0.0.1:8000/api";
  const PROVINCIA_DEFAULT = 14;
  const LOCALIDAD_DEFAULT = 3622;

  const provinciaSelect = document.getElementById("provincia");
  const localidadSelect = document.getElementById("ciudad");
  const form            = document.getElementById("alumnoForm");
  if (!form) return;

  // ===========================
  // DETECTAR MODO: alta o edición
  // ===========================
  const params     = new URLSearchParams(window.location.search);
  const editarId   = params.get("editar");   // ?editar=ID → modo edición
  const modoEditar = !!editarId;

  let alumnoEditando = null;

  // Cambiar título si es edición
  if (modoEditar) {
    const h1 = document.querySelector(".form-header h1");
    if (h1) h1.textContent = "Editar Alumno";
  }

  // ===========================
  // LIMPIAR ERRORES EN TIEMPO REAL
  // ===========================
  let dniTimeout   = null;
  let emailTimeout = null;

  form.querySelectorAll("input, select").forEach(input => {
    input.addEventListener("input", () => {
      const name  = input.name;
      const value = input.value.trim();
      switch (name) {
        case "dni":      if (/^[0-9]{8}$/.test(value))     limpiarErrorCampo("dni");      break;
        case "email":    if (/^\S+@\S+\.\S+$/.test(value)) limpiarErrorCampo("email");    break;
        case "prefijo":  if (/^[0-9]{2,5}$/.test(value))   limpiarErrorCampo("prefijo");  break;
        case "telefono": if (/^[0-9]{6,15}$/.test(value))  limpiarErrorCampo("telefono"); break;
        default:         if (value !== "")                  limpiarErrorCampo(name);       break;
      }
    });
  });

  let isSubmitting = false;

  const apellidoInput     = form.querySelector('[name="apellido"]');
  const dniInput          = form.querySelector('[name="dni"]');
  const legajoInput       = form.querySelector('[name="legajo"]');
  let legajoEditadoManual = false;

  legajoInput.addEventListener("input", () => { legajoEditadoManual = true; });

  function generarLegajoAutomatico() {
    if (legajoEditadoManual || modoEditar) return;
    const apellido = apellidoInput.value.trim();
    const dni      = dniInput.value.trim();
    if (apellido && dni && /^[0-9]{7,8}$/.test(dni)) {
      legajoInput.value = `${apellido.charAt(0).toUpperCase()}-${dni}`;
    }
  }

  apellidoInput.addEventListener("input", generarLegajoAutomatico);
  dniInput.addEventListener("input",      generarLegajoAutomatico);

  // ===========================
  // CARGAR AÑOS INGRESO
  // ===========================
  function cargarAniosIngreso(selectId = null) {
    const select = selectId
      ? document.getElementById(selectId)
      : document.querySelector('[name="anio_ingreso"]');
    if (!select) return;
    const anioActual = new Date().getFullYear();
    select.innerHTML = `
      <option value="" disabled hidden></option>
      <option value="${anioActual - 1}">${anioActual - 1}</option>
      <option value="${anioActual}">${anioActual}</option>
      <option value="${anioActual + 1}">${anioActual + 1}</option>
    `;
    if (!selectId) select.value = anioActual;
  }

  // ===========================
  // PROVINCIAS Y LOCALIDADES
  // ===========================
  async function cargarProvincias(provinciaSeleccionada = null) {
    if (!provinciaSelect) return;
    provinciaSelect.innerHTML = `<option value="" selected disabled hidden></option>`;
    try {
      const response   = await authFetch(`${API}/provincias/`);
      if (!response) return;
      const provincias = await response.json();
      provincias.forEach(prov => {
        const option       = document.createElement("option");
        option.value       = prov.id_prov;
        option.textContent = prov.nombre;
        provinciaSelect.appendChild(option);
      });
      const provId = provinciaSeleccionada || PROVINCIA_DEFAULT;
      provinciaSelect.value = provId;
      await cargarLocalidades(provId);
    } catch (error) {
      console.error("Error cargando provincias:", error);
    }
  }

  async function cargarLocalidades(provinciaId, localidadSeleccionada = null) {
    if (!localidadSelect) return;
    localidadSelect.innerHTML = `<option value="" selected disabled hidden></option>`;
    if (!provinciaId) return;
    try {
      const response    = await authFetch(`${API}/localidades/?provincia=${provinciaId}`);
      if (!response) return;
      const localidades = await response.json();
      localidades.forEach(loc => {
        const option       = document.createElement("option");
        option.value       = loc.id_loc;
        option.textContent = loc.nombre;
        localidadSelect.appendChild(option);
      });
      if (localidadSeleccionada) {
        localidadSelect.value = localidadSeleccionada;
      } else if (parseInt(provinciaId) === PROVINCIA_DEFAULT) {
        localidadSelect.value = LOCALIDAD_DEFAULT;
      }
    } catch (error) {
      console.error("Error cargando localidades:", error);
    }
  }

  provinciaSelect.addEventListener("change", e => {
    cargarLocalidades(e.target.value);
    limpiarErrorCampo("provincia");
  });
  localidadSelect.addEventListener("change", () => limpiarErrorCampo("ciudad"));

  // ===========================
  // CARRERAS
  // ===========================
  async function cargarCarreras(selectId = "id_carrera", excluirIds = []) {
    const select = document.getElementById(selectId);
    if (!select) return;
    select.innerHTML = `<option value="" selected disabled hidden>Seleccionar</option>`;
    try {
      const response = await authFetch(`${API}/carreras/`);
      if (!response) return;
      const carreras  = await response.json();
      carreras
        .filter(c => !excluirIds.includes(c.id_carrera))
        .forEach(carrera => {
          const option       = document.createElement("option");
          option.value       = carrera.id_carrera;
          option.textContent = carrera.descripcion;
          select.appendChild(option);
        });
    } catch (error) {
      console.error("Error cargando carreras:", error);
    }
  }

  // ===========================
  // PRECARGAR DATOS EN MODO EDICIÓN
  // ===========================
  async function cargarDatosAlumno(id) {
    try {
      const resp = await authFetch(`${API}/alumnos/${id}/`);
      if (!resp || !resp.ok) return;
      const alumno = await resp.json();
      alumnoEditando = alumno;

      // Datos personales
      form.querySelector('[name="nombre"]').value          = alumno.nombre          || "";
      form.querySelector('[name="apellido"]').value        = alumno.apellido        || "";
      form.querySelector('[name="dni"]').value             = alumno.dni             || "";
      form.querySelector('[name="cuit"]').value            = alumno.cuit            || "";
      form.querySelector('[name="fecha_nacimiento"]').value = alumno.fecha_nacimiento || "";
      form.querySelector('[name="legajo"]').value          = alumno.legajo          || "";
      legajoEditadoManual = true; // No generar legajo automático

      // Contacto
      form.querySelector('[name="direccion"]').value  = alumno.direccion  || "";
      form.querySelector('[name="numero"]').value     = alumno.numero     || "";
      form.querySelector('[name="departamento"]').value = alumno.departamento || "";
      form.querySelector('[name="piso"]').value       = alumno.piso       || "";
      form.querySelector('[name="prefijo"]').value    = alumno.prefijo    || "";
      form.querySelector('[name="telefono"]').value   = alumno.telefono   || "";
      form.querySelector('[name="email"]').value      = alumno.email      || "";

      // Provincia y localidad — cargar correctamente
      await cargarProvincias();
      if (alumno.ciudad) {
        localidadSelect.value = alumno.ciudad;
      }

      // Ocultar sección académica en modo edición (no se edita carrera desde acá)
      const seccionAcademica = document.querySelector(".form-section:last-of-type");
      if (seccionAcademica) {
        const h2 = seccionAcademica.querySelector("h2");
        if (h2 && h2.textContent.includes("académico")) {
          seccionAcademica.style.display = "none";
        }
      }

    } catch (err) {
      console.error("Error cargando datos del alumno:", err);
    }
  }

  // ===========================
  // ERRORES
  // ===========================
  function limpiarErrores() {
    document.querySelectorAll(".error-msg").forEach(e => e.innerText = "");
    document.querySelectorAll(".input-field").forEach(f => f.classList.remove("has-error"));
  }

  function setError(name, msg) {
    const span    = document.getElementById("error-" + name);
    const input   = form.querySelector(`[name="${name}"]`);
    if (!input) return;
    const wrapper = input.closest(".input-field");
    if (span) span.innerText = msg;
    if (wrapper) wrapper.classList.add("has-error");
  }

  function limpiarErrorCampo(name) {
    const span    = document.getElementById("error-" + name);
    const input   = form.querySelector(`[name="${name}"]`);
    if (!input) return;
    const wrapper = input.closest(".input-field");
    if (span)    span.innerText = "";
    if (wrapper) wrapper.classList.remove("has-error");
  }

  // ===========================
  // MODAL DNI — alumno existente
  // ===========================
  let alumnoEncontrado = null;

  function aclararColor(hex, factor) {
    hex = hex.replace("#", "");
    const r = Math.min(255, parseInt(hex.substring(0, 2), 16) + factor);
    const g = Math.min(255, parseInt(hex.substring(2, 4), 16) + factor);
    const b = Math.min(255, parseInt(hex.substring(4, 6), 16) + factor);
    return `rgb(${r},${g},${b})`;
  }

  function mostrarModalDNI(alumno) {
    alumnoEncontrado = alumno;
    const modal = document.getElementById("dni-modal");
    if (!modal) return;

    document.getElementById("dni-alumno-info").innerHTML = `
      <div class="nombre-alumno">${alumno.apellido}, ${alumno.nombre}</div>
      <div class="dato-alumno">DNI: ${alumno.dni}</div>
      <div class="dato-alumno">Legajo: ${alumno.legajo || "—"}</div>
      <div class="dato-alumno">Email: ${alumno.email || "—"}</div>
    `;

    const carreras = alumno.carreras || [];
    const listaEl  = document.getElementById("carreras-actuales-lista");

    if (carreras.length === 0) {
      listaEl.innerHTML = `<span style="color:#888; font-size:0.85rem;">Sin carreras registradas.</span>`;
    } else {
      listaEl.innerHTML = carreras.map(c => {
        const fondo = aclararColor(c.color || "#1E3A8A", 150);
        return `
          <span class="carrera-chip" style="background:${fondo}; color:${c.color || '#1E3A8A'};">
            <span class="dot" style="background:${c.color || '#1E3A8A'};"></span>
            ${c.descripcion}
            <span style="opacity:0.6; font-weight:400;">${c.activa ? "Activa" : "Inactiva"}</span>
          </span>
        `;
      }).join("");
    }

    const idsActuales = carreras.map(c => c.id_carrera);
    cargarCarreras("nueva-carrera-select", idsActuales);
    cargarAniosIngreso("nueva-carrera-anio");
    document.getElementById("msgAgregarCarrera").innerHTML = "";
    modal.classList.remove("hidden");
  }

  document.getElementById("ver-ficha-btn")?.addEventListener("click", () => {
    if (alumnoEncontrado) window.location.href = `/alumnos/${alumnoEncontrado.id_alumno}/`;
  });

  document.getElementById("cerrar-modal-btn")?.addEventListener("click", () => {
    document.getElementById("dni-modal")?.classList.add("hidden");
    alumnoEncontrado = null;
  });

  document.getElementById("agregar-carrera-btn")?.addEventListener("click", async () => {
    if (!alumnoEncontrado) return;

    const carreraId   = parseInt(document.getElementById("nueva-carrera-select").value);
    const anioIngreso = parseInt(document.getElementById("nueva-carrera-anio").value);
    const msg         = document.getElementById("msgAgregarCarrera");

    if (!carreraId)   { msg.innerHTML = `<span style="color:#dc2626;">Seleccioná una carrera.</span>`;       return; }
    if (!anioIngreso) { msg.innerHTML = `<span style="color:#dc2626;">Seleccioná el año de ingreso.</span>`; return; }

    const btn = document.getElementById("agregar-carrera-btn");
    btn.disabled = true;
    msg.innerHTML = `<span style="color:#888;">Guardando...</span>`;

    try {
      const resp = await authFetch(`${API}/carreras-cursadas/`, {
        method:  "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          alumno:       alumnoEncontrado.id_alumno,
          carrera:      carreraId,
          id_estado:    1,
          anio_ingreso: anioIngreso,
        }),
      });

      if (resp && resp.ok) {
        msg.innerHTML = `<span style="color:#16a34a;">✓ Carrera agregada correctamente.</span>`;
        setTimeout(async () => {
          const r2 = await authFetch(`${API}/alumnos/${alumnoEncontrado.id_alumno}/`);
          if (r2 && r2.ok) {
            alumnoEncontrado = await r2.json();
            mostrarModalDNI(alumnoEncontrado);
            document.getElementById("msgAgregarCarrera").innerHTML =
              `<span style="color:#16a34a;">✓ Carrera agregada correctamente.</span>`;
          }
        }, 800);
      } else if (resp) {
        const err = await resp.json();
        msg.innerHTML = `<span style="color:#dc2626;">${err.detail || err.error || "No se pudo agregar la carrera."}</span>`;
      }
    } catch (e) {
      msg.innerHTML = `<span style="color:#dc2626;">Error de conexión.</span>`;
    } finally {
      btn.disabled = false;
    }
  });

  // ===========================
  // MODAL INSCRIPCION
  // ===========================
  function mostrarModalInscripcion(alumnoId, carreraId, nombreAlumno, nombreCarrera) {
    const modal = document.getElementById("inscripcion-modal");
    if (!modal) return;
    document.getElementById("inscripcion-alumno-nombre").textContent  = nombreAlumno;
    document.getElementById("inscripcion-carrera-nombre").textContent = nombreCarrera;
    modal.classList.remove("hidden");

    document.getElementById("inscripcion-pagar-btn").onclick = () => {
      modal.classList.add("hidden");
      window.location.href = `/cobros/cobros/?alumno=${alumnoId}&carrera=${carreraId}`;
    };

    document.getElementById("inscripcion-despues-btn").onclick = () => {
      modal.classList.add("hidden");
      window.location.href = "/alumnos/alumnos/";
    };
  }

  // ===========================
  // VALIDACIÓN
  // ===========================
  function validar() {
    limpiarErrores();
    let valido = true;

    // En modo edición no se validan los campos académicos
    const camposObligatorios = modoEditar
      ? ["nombre", "apellido", "dni", "fecha_nacimiento", "direccion", "numero", "prefijo", "telefono", "email"]
      : ["nombre", "apellido", "dni", "fecha_nacimiento", "direccion", "numero", "prefijo", "telefono", "email", "id_carrera", "anio_ingreso"];

    camposObligatorios.forEach(nombreCampo => {
      const input = form.querySelector(`[name="${nombreCampo}"]`);
      if (!input) return;
      const wrapper = input.closest(".input-field");
      if (!input.value.trim()) {
        setError(nombreCampo, "Campo obligatorio");
        if (wrapper) wrapper.classList.add("has-error");
        valido = false;
      } else {
        if (wrapper) wrapper.classList.remove("has-error");
      }
    });

    const dni = form.querySelector('[name="dni"]')?.value.trim();
    if (dni && !/^[0-9]{7,8}$/.test(dni)) {
      setError("dni", "Debe tener 7 u 8 dígitos");
      valido = false;
    }

    const email = form.querySelector('[name="email"]')?.value.trim();
    if (email && !/^\S+@\S+\.\S+$/.test(email)) {
      setError("email", "Correo inválido");
      valido = false;
    }

    const prefijo = form.querySelector('[name="prefijo"]')?.value;
    if (prefijo && !/^[0-9]{2,5}$/.test(prefijo.trim())) {
      setError("prefijo", "Prefijo inválido");
      valido = false;
    }

    const telefono = form.querySelector('[name="telefono"]')?.value;
    if (telefono && !/^[0-9]{6,15}$/.test(telefono.trim())) {
      setError("telefono", "Teléfono inválido");
      valido = false;
    }

    return valido;
  }

  // ===========================
  // SUBMIT
  // ===========================
  form.addEventListener("submit", async e => {
    e.preventDefault();
    if (isSubmitting) return;
    isSubmitting = true;

    if (!validar()) { isSubmitting = false; return; }

    const data = Object.fromEntries(new FormData(form));
    ["direccion", "numero", "departamento", "piso"].forEach(campo => {
      if (!data[campo]) delete data[campo];
    });
    delete data.provincia;
    if (data.id_carrera)   data.id_carrera   = parseInt(data.id_carrera);
    if (data.anio_ingreso) data.anio_ingreso  = parseInt(data.anio_ingreso);

    try {
      let response;

      if (modoEditar) {
        // PATCH — actualizar alumno existente
        // Preservar el estado actual del alumno al editar
        if (!data.id_estado && alumnoEditando?.estado_actual) {
          data.id_estado = alumnoEditando.estado_actual;
        }

        response = await authFetch(`${API}/alumnos/${editarId}/`, {
          method:  "PATCH",
          headers: { "Content-Type": "application/json" },
          body:    JSON.stringify(data),
        });

        if (response && response.ok) {
          showAlert("Datos actualizados correctamente ✅", "success");
          setTimeout(() => window.location.href = `/alumnos/${editarId}/`, 1200);
        } else if (response) {
          const error = await response.json();
          if (error.email) setError("email", error.email[0]);
          if (error.dni)   setError("dni",   error.dni[0]);
        }

      } else {
        // POST — crear alumno nuevo
        response = await authFetch(`${API}/alumnos/`, {
          method:  "POST",
          headers: { "Content-Type": "application/json" },
          body:    JSON.stringify(data),
        });

        if (response && response.ok) {
          const alumno = await response.json();
          const carreraSelect = document.getElementById("id_carrera");
          const nombreCarrera = carreraSelect?.options[carreraSelect.selectedIndex]?.text || "";
          mostrarModalInscripcion(
            alumno.id_alumno, data.id_carrera,
            `${alumno.apellido}, ${alumno.nombre}`, nombreCarrera
          );
        } else if (response) {
          const error = await response.json();
          if (error.email) setError("email", error.email[0]);
          if (error.dni)   setError("dni",   error.dni[0]);
        }
      }

    } catch (err) {
      console.error("Error de conexión:", err);
    }

    isSubmitting = false;
  });

  // ===========================
  // VALIDACIÓN EN TIEMPO REAL
  // ===========================
  const emailInput = form.querySelector('[name="email"]');
  emailInput?.addEventListener("input", () => {
    const email = emailInput.value.trim();
    clearTimeout(emailTimeout);
    if (!/^\S+@\S+\.\S+$/.test(email)) return;
    emailTimeout = setTimeout(async () => {
      const response = await authFetch(`${API}/alumnos/?email=${email}`);
      if (!response) return;
      const alumnos  = await response.json();
      if (Array.isArray(alumnos) && alumnos.length > 0) {
        // En modo edición ignorar si el email es del mismo alumno
        if (modoEditar && alumnos[0].id_alumno === parseInt(editarId)) return;
        setError("email", "Ya existe un alumno con este correo");
      } else {
        limpiarErrorCampo("email");
      }
    }, 400);
  });

  // Solo verificar DNI duplicado en modo alta
  if (!modoEditar) {
    dniInput?.addEventListener("input", () => {
      const dni = dniInput.value.trim();
      clearTimeout(dniTimeout);
      if (!/^[0-9]{8}$/.test(dni)) return;
      dniTimeout = setTimeout(async () => {
        const response = await authFetch(`${API}/alumnos/?dni=${dni}`);
        if (!response) return;
        const alumnos  = await response.json();
        if (Array.isArray(alumnos) && alumnos.length > 0) {
          mostrarModalDNI(alumnos[0]);
        }
      }, 400);
    });
  }

  // ===========================
  // INICIALIZAR
  // ===========================
  if (modoEditar) {
    await cargarDatosAlumno(editarId);
  } else {
    await cargarProvincias();
    cargarCarreras();
    cargarAniosIngreso();
  }
});