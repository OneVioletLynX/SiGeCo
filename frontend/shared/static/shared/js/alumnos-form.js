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

  let dniTimeout   = null;
  let emailTimeout = null;

  const PROVINCIA_DEFAULT = 14;
  const LOCALIDAD_DEFAULT = 3622;
  const API               = "http://localhost:8000/api";

  const provinciaSelect = document.getElementById("provincia");
  const localidadSelect = document.getElementById("ciudad");
  const form            = document.getElementById("alumnoForm");

  if (!form) return;

  // Limpiar errores en tiempo real
  form.querySelectorAll("input, select").forEach(input => {
    input.addEventListener("input", () => {
      const name  = input.name;
      const value = input.value.trim();

      switch (name) {
        case "dni":      if (/^[0-9]{8}$/.test(value))      limpiarErrorCampo("dni");      break;
        case "email":    if (/^\S+@\S+\.\S+$/.test(value))  limpiarErrorCampo("email");    break;
        case "prefijo":  if (/^[0-9]{2,5}$/.test(value))    limpiarErrorCampo("prefijo");  break;
        case "telefono": if (/^[0-9]{6,15}$/.test(value))   limpiarErrorCampo("telefono"); break;
        default:         if (value !== "")                   limpiarErrorCampo(name);       break;
      }
    });
  });

  let isSubmitting = false;

  const apellidoInput         = form.querySelector('[name="apellido"]');
  const dniInput              = form.querySelector('[name="dni"]');
  const legajoInput           = form.querySelector('[name="legajo"]');
  let   legajoEditadoManual   = false;

  legajoInput.addEventListener("input", () => { legajoEditadoManual = true; });

  function generarLegajoAutomatico() {
    if (legajoEditadoManual) return;
    const apellido = apellidoInput.value.trim();
    const dni      = dniInput.value.trim();
    if (apellido && dni && /^[0-9]{7,8}$/.test(dni)) {
      legajoInput.value = `${apellido.charAt(0).toUpperCase()}-${dni}`;
    }
  }

  apellidoInput.addEventListener("input", generarLegajoAutomatico);
  dniInput.addEventListener("input",      generarLegajoAutomatico);

  function cargarAniosIngreso() {
    const select = document.querySelector('[name="anio_ingreso"]');
    if (!select) return;
    const anioActual  = new Date().getFullYear();
    select.innerHTML  = `
      <option value="" disabled hidden></option>
      <option value="${anioActual}">${anioActual}</option>
      <option value="${anioActual + 1}">${anioActual + 1}</option>
    `;
    select.value = anioActual;
  }

  async function cargarProvincias() {
    if (!provinciaSelect) return;
    provinciaSelect.innerHTML = `<option value="" selected disabled hidden></option>`;
    try {
      const response  = await authFetch(`${API}/provincias/`);
      if (!response) return;
      const provincias = await response.json();
      provincias.forEach(prov => {
        const option   = document.createElement("option");
        option.value   = prov.id_prov;
        option.textContent = prov.nombre;
        provinciaSelect.appendChild(option);
      });
      provinciaSelect.value = PROVINCIA_DEFAULT;
      await cargarLocalidades(PROVINCIA_DEFAULT);
    } catch (error) {
      console.error("Error cargando provincias:", error);
    }
  }

  async function cargarLocalidades(provinciaId) {
    if (!localidadSelect) return;
    localidadSelect.innerHTML = `<option value="" selected disabled hidden></option>`;
    if (!provinciaId) return;
    try {
      const response   = await authFetch(`${API}/localidades/?provincia=${provinciaId}`);
      if (!response) return;
      const localidades = await response.json();
      localidades.forEach(loc => {
        const option       = document.createElement("option");
        option.value       = loc.id_loc;
        option.textContent = loc.nombre;
        localidadSelect.appendChild(option);
      });
      if (parseInt(provinciaId) === PROVINCIA_DEFAULT) {
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

  async function cargarCarreras() {
    const select = document.getElementById("id_carrera");
    if (!select) return;
    select.innerHTML = `<option value="" selected disabled hidden>Seleccionar</option>`;
    try {
      const response = await authFetch(`${API}/carreras/`);
      if (!response) return;
      const carreras  = await response.json();
      carreras.forEach(carrera => {
        const option       = document.createElement("option");
        option.value       = carrera.id_carrera;
        option.textContent = carrera.descripcion;
        select.appendChild(option);
      });
    } catch (error) {
      console.error("Error cargando carreras:", error);
    }
  }

  // ===============================
  // ERRORES
  // ===============================
  function limpiarErrores() {
    document.querySelectorAll(".error-msg").forEach(e => e.innerText = "");
    document.querySelectorAll(".input-field").forEach(f => f.classList.remove("has-error"));
  }

  function setError(name, msg) {
    const span    = document.getElementById("error-" + name);
    const input   = form.querySelector(`[name="${name}"]`);
    const wrapper = input.closest(".input-field");
    if (span) span.innerText = msg;
    wrapper.classList.add("has-error");
  }

  function limpiarErrorCampo(name) {
    const span    = document.getElementById("error-" + name);
    const input   = form.querySelector(`[name="${name}"]`);
    if (!input) return;
    const wrapper = input.closest(".input-field");
    if (span) span.innerText = "";
    wrapper.classList.remove("has-error");
  }

  function mostrarFichaAlumno(alumno) {
    const modal = document.getElementById("dni-modal");
    const info  = document.getElementById("dni-alumno-info");
    info.innerHTML = `
      <p><b>Nombre:</b> ${alumno.nombre} ${alumno.apellido}</p>
      <p><b>DNI:</b> ${alumno.dni}</p>
      <p><b>Email:</b> ${alumno.email}</p>
      <p><b>Legajo:</b> ${alumno.legajo}</p>
    `;
    document.getElementById("ver-ficha-btn").onclick      = () => { window.location.href = `/alumnos/${alumno.id_alumno}/`; };
    document.getElementById("agregar-carrera-btn").onclick = () => { window.location.href = `/alumnos/${alumno.id_alumno}/agregar-carrera/`; };
    document.getElementById("cerrar-modal-btn").onclick   = () => { modal.classList.add("hidden"); };
    modal.classList.remove("hidden");
  }

  // ===============================
  // VALIDACIÓN
  // ===============================
  function validar() {
    limpiarErrores();
    let valido = true;

    const camposObligatorios = [
      "nombre", "apellido", "dni", "fecha_nacimiento",
      "direccion", "numero", "prefijo", "telefono",
      "email", "id_carrera", "anio_ingreso",
    ];

    camposObligatorios.forEach(nombreCampo => {
      const input   = form.querySelector(`[name="${nombreCampo}"]`);
      const wrapper = input.closest(".input-field");
      if (!input.value.trim()) {
        setError(nombreCampo, "Campo obligatorio");
        wrapper.classList.add("has-error");
        valido = false;
      } else {
        wrapper.classList.remove("has-error");
      }
    });

    const dni = form.dni.value.trim();
    if (dni && !/^[0-9]{7,8}$/.test(dni)) {
      setError("dni", "Debe tener 7 u 8 dígitos");
      form.dni.closest(".input-field").classList.add("has-error");
      valido = false;
    }

    const email = form.email.value.trim();
    if (email && !/^\S+@\S+\.\S+$/.test(email)) {
      setError("email", "Correo inválido");
      form.email.closest(".input-field").classList.add("has-error");
      valido = false;
    }

    if (form.prefijo.value && !/^[0-9]{2,5}$/.test(form.prefijo.value.trim())) {
      setError("prefijo", "Prefijo inválido");
      form.prefijo.closest(".input-field").classList.add("has-error");
      valido = false;
    }

    if (form.telefono.value && !/^[0-9]{6,15}$/.test(form.telefono.value.trim())) {
      setError("telefono", "Teléfono inválido");
      form.telefono.closest(".input-field").classList.add("has-error");
      valido = false;
    }

    return valido;
  }

  // ===============================
  // SUBMIT
  // ===============================
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

    if (data.id_carrera)  data.id_carrera  = parseInt(data.id_carrera);
    if (data.anio_ingreso) data.anio_ingreso = parseInt(data.anio_ingreso);

    try {
      const response = await authFetch(`${API}/alumnos/`, {
        method:  "POST",
        headers: { "Content-Type": "application/json" },
        body:    JSON.stringify(data),
      });

      if (response && response.ok) {
        window.location.href = "/alumnos/alumnos/";
      } else if (response) {
        const error = await response.json();
        if (error.email) setError("email", error.email[0]);
      }
    } catch (err) {
      console.error("Error de conexión:", err);
    }

    isSubmitting = false;
  });

  // ===============================
  // VALIDACIÓN EN TIEMPO REAL — EMAIL Y DNI
  // ===============================
  const emailInput = form.querySelector('[name="email"]');

  emailInput.addEventListener("input", () => {
    const email = emailInput.value.trim();
    clearTimeout(emailTimeout);
    if (!/^\S+@\S+\.\S+$/.test(email)) return;
    emailTimeout = setTimeout(async () => {
      const response = await authFetch(`${API}/alumnos/?email=${email}`);
      if (!response) return;
      const alumnos  = await response.json();
      if (alumnos.length > 0) {
        setError("email", "Ya existe un alumno con este correo");
      } else {
        limpiarErrorCampo("email");
      }
    }, 400);
  });

  dniInput.addEventListener("input", () => {
    const dni = dniInput.value.trim();
    clearTimeout(dniTimeout);
    if (!/^[0-9]{8}$/.test(dni)) return;
    dniTimeout = setTimeout(async () => {
      const response = await authFetch(`${API}/alumnos/?dni=${dni}`);
      if (!response) return;
      const alumnos  = await response.json();
      if (alumnos.length > 0) mostrarFichaAlumno(alumnos[0]);
    }, 400);
  });

  // ===============================
  // INICIALIZAR
  // ===============================
  cargarCarreras();
  cargarAniosIngreso();
  cargarProvincias();
});