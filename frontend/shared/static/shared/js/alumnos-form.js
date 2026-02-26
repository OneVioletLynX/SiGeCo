document.addEventListener("DOMContentLoaded", () => {

  const form = document.getElementById("alumnoForm");
  if (!form) return;
    form.querySelectorAll("input, select").forEach(input => {

  input.addEventListener("input", () => {

    const name = input.name;
    const value = input.value.trim();

    switch (name) {

      case "dni":
        if (/^[0-9]{8}$/.test(value)) {
          limpiarErrorCampo("dni");
        }
        break;

      case "email":
        if (/^\S+@\S+\.\S+$/.test(value)) {
          limpiarErrorCampo("email");
        }
        break;

      case "prefijo":
        if (/^[0-9]{2,5}$/.test(value)) {
          limpiarErrorCampo("prefijo");
        }
        break;

      case "telefono":
        if (/^[0-9]{6,15}$/.test(value)) {
          limpiarErrorCampo("telefono");
        }
        break;

      default:
        if (value !== "") {
          limpiarErrorCampo(name);
        }
        break;
    }

  });

});
  let isSubmitting = false;

  const apellidoInput = form.querySelector('[name="apellido"]');
const dniInput = form.querySelector('[name="dni"]');
const legajoInput = form.querySelector('[name="legajo"]');

let legajoEditadoManualmente = false;

// Detectar si el usuario escribió en legajo
legajoInput.addEventListener("input", () => {
  legajoEditadoManualmente = true;
});

function generarLegajoAutomatico() {
  if (legajoEditadoManualmente) return;

  const apellido = apellidoInput.value.trim();
  const dni = dniInput.value.trim();

  if (apellido && dni && /^[0-9]{7,8}$/.test(dni)) {
    const primeraLetra = apellido.charAt(0).toUpperCase();
    legajoInput.value = `${primeraLetra}-${dni}`;
  }
}

function cargarAniosIngreso() {
  const select = document.querySelector('[name="anio_ingreso"]');
  if (!select) return;

  const anioActual = new Date().getFullYear();

  select.innerHTML = `
    <option value="" disabled hidden></option>
    <option value="${anioActual}">${anioActual}</option>
    <option value="${anioActual + 1}">${anioActual + 1}</option>
  `;

  select.value = anioActual;
}

async function cargarCarreras() {
  const select = document.getElementById("id_carrera");
  if (!select) return;

  select.innerHTML = `<option value="" selected disabled hidden>Seleccionar</option>`;

  try {
    const response = await fetch("http://localhost:8000/api/carreras/");
    const carreras = await response.json();

    carreras.forEach(carrera => {
      const option = document.createElement("option");
      option.value = carrera.id_carrera;
      option.textContent = carrera.descripcion;
      select.appendChild(option);
    });

  } catch (error) {
    console.error("Error cargando carreras:", error);
  }
}

// Escuchar cambios en apellido y dni
apellidoInput.addEventListener("input", generarLegajoAutomatico);
dniInput.addEventListener("input", generarLegajoAutomatico);
  // ===============================
  // ERRORES
  // ===============================
function limpiarErrores() {
  document.querySelectorAll(".error-msg").forEach(e => e.innerText = "");
  document.querySelectorAll(".input-field").forEach(f => f.classList.remove("has-error"));
}

function setError(name, msg) {
  const span = document.getElementById("error-" + name);
  const input = form.querySelector(`[name="${name}"]`);
  const wrapper = input.closest(".input-field");

  if (span) span.innerText = msg;
  wrapper.classList.add("has-error");
}

function limpiarErrorCampo(name) {
  const span = document.getElementById("error-" + name);
  const input = form.querySelector(`[name="${name}"]`);
  const wrapper = input.closest(".input-field");

  if (span) span.innerText = "";
  wrapper.classList.remove("has-error");
}
  // ===============================
  // VALIDACIÓN
  // ===============================
function validar() {
  limpiarErrores();
  let valido = true;

  const camposObligatorios = [
    "nombre",
    "apellido",
    "dni",
    "fecha_nacimiento",
    "direccion",
    "numero",
    "prefijo",
    "telefono",
    "email",
    "id_carrera",
    "anio_ingreso"
  ];

  camposObligatorios.forEach(nombreCampo => {
    const input = form.querySelector(`[name="${nombreCampo}"]`);
    const wrapper = input.closest(".input-field");

    if (!input.value.trim()) {
      setError(nombreCampo, "Campo obligatorio");
      wrapper.classList.add("has-error");
      valido = false;
    } else {
      wrapper.classList.remove("has-error");
    }
  });

  // Validación específica DNI
  const dni = form.dni.value.trim();
  if (dni && !/^[0-9]{7,8}$/.test(dni)) {
    setError("dni", "Debe tener 7 u 8 dígitos");
    form.dni.closest(".input-field").classList.add("has-error");
    valido = false;
  }

  // Validación email
  const email = form.email.value.trim();
  if (email && !/^\S+@\S+\.\S+$/.test(email)) {
    setError("email", "Correo inválido");
    form.email.closest(".input-field").classList.add("has-error");
    valido = false;
  }

  // Prefijo
  if (form.prefijo.value && !/^[0-9]{2,5}$/.test(form.prefijo.value.trim())) {
    setError("prefijo", "Prefijo inválido");
    form.prefijo.closest(".input-field").classList.add("has-error");
    valido = false;
  }

  // Teléfono
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

    if (!validar()) {
      isSubmitting = false;
      return;
    }

    const data = Object.fromEntries(new FormData(form));
    data.id_carrera = parseInt(data.id_carrera || "0");
    data.id_estado = parseInt(data.id_estado || "0");

    const response = await fetch("http://localhost:8000/api/alumnos/", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data)
    });

    if (response.ok) {
      window.location.href = "/alumnos/alumnos/";
    }

    isSubmitting = false;
  });
  cargarCarreras();
cargarAniosIngreso();
});