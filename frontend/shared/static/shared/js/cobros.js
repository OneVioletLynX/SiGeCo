// --- Buscador + Carga dinámica de meses + Registrar Pago ---
(function () {
  const metaApi = document.querySelector('meta[name="api-base"]');
  const API_BASE =
    (window.API_BASE && String(window.API_BASE).trim()) ||
    (metaApi ? metaApi.content.trim() : "") ||
    "http://127.0.0.1:8000";

  let alumnoSeleccionado = null;
  let carreraSeleccionadaId = null;

  const CONCEPTO_CUOTA_ID = 1; // cuota mensual
  const CONCEPTO_INSCRIPCION_ID = 2; // inscripción

  document.addEventListener("DOMContentLoaded", () => {


      function formatearFecha(fechaISO) {
      if (!fechaISO) return "";

      const f = new Date(fechaISO);

      const dia = String(f.getDate()).padStart(2, "0");
      const mes = String(f.getMonth() + 1).padStart(2, "0");
      const anio = f.getFullYear();

      const hora = String(f.getHours()).padStart(2, "0");
      const minuto = String(f.getMinutes()).padStart(2, "0");

      return `${dia}/${mes}/${anio} ${hora}:${minuto}`;
    }

    const buscador = document.getElementById("buscador");
    const sugerencias = document.getElementById("sugerencias");

    const modal = document.getElementById("altaModal");
    const btnAbrir = document.getElementById("btnAgregar");
    const btnCerrar = document.querySelector(".modal .close");
    const metodoSelect = document.getElementById("metodo_pago");
    const campoComprobante = document.getElementById("campo-comprobante");
    const campoTarjeta = document.getElementById("campo-tarjeta");
    const form = document.getElementById("cobroForm");
    const contenedorMeses = document.querySelector(".meses-container");

    let timeout = null;

    metodoSelect.addEventListener("change", function () {
      const metodo = metodoSelect.value;

      // Ocultar todo por defecto
      campoComprobante.classList.add("hidden");
      campoTarjeta.classList.add("hidden");

      if (metodo === "2") {  // ejemplo: 2 = TRANSFERENCIA
        campoComprobante.classList.remove("hidden");
      }

      if (metodo === "3") {  // ejemplo: 3 = TARJETA
        campoTarjeta.classList.remove("hidden");
      }
    });


    // =====================================
    // BUSCADOR DE ALUMNOS
    // =====================================
    buscador.addEventListener("input", () => {
      const q = buscador.value.trim();
      if (q.length < 2) {
        sugerencias.innerHTML = "";
        sugerencias.style.display = "none";
        return;
      }

      buscarAlumnos(q);

    });

    async function buscarAlumnos(q) {
      try {
        const url = `${API_BASE}/api/alumnos/?search=${encodeURIComponent(q)}`;
        const resp = await fetch(url);
        const data = await resp.json();
        const alumnos = data.results || data || [];

        sugerencias.innerHTML = "";
        if (!alumnos.length) {
          sugerencias.innerHTML = "<div class='no-results'>Sin resultados</div>";
          sugerencias.style.display = "block";
          return;
        }


        alumnos.forEach((al) => {
        const item = document.createElement("div");
        item.classList.add("suggestion-item");
        item.textContent = `${al.apellido}, ${al.nombre}`;
        item.addEventListener("click", () => seleccionarAlumno(al));
        sugerencias.appendChild(item);
        });

        sugerencias.style.display = "block";
      } catch (err) {
        sugerencias.innerHTML = "<div class='no-results'>Sin resultados</div>";

      }
    }

    async function seleccionarAlumno(alumno) {
      buscador.value = `${alumno.apellido}, ${alumno.nombre}`;
      sugerencias.innerHTML = "";
      sugerencias.style.display = "none";

      alumnoSeleccionado = alumno;
      carreraSeleccionadaId = alumno.carrera_actual;

      // === MOSTRAR BOTÓN AGREGAR ===
      const btnAgregar = document.getElementById("btnAgregar");
      if (btnAgregar) {
        btnAgregar.style.display = "flex";
      }

      cargarPagos(alumno.id_alumno);
    }


    // =====================================
    // CARGAR PAGOS EXISTENTES
    // =====================================
    async function cargarPagos(alumnoId) {
      try {
        const url = `${API_BASE}/api/pago/?alumno=${alumnoId}`;
        const resp = await fetch(url);
        const pagos = await resp.json();

        const tbody =
          document.getElementById("tabla-cobros-body") ||
          document.getElementById("tabla-cobros");

        tbody.innerHTML = ""; 

      pagos.forEach((pago) => {
        const detalles = pago.detalles || [];

        detalles.forEach((det) => {
          const tr = document.createElement("tr");

          tr.innerHTML = `
            <td>${det.anio}</td>
            <td>${det.mes}</td>
            <td>$${det.importe}</td>
            <td>${formatearFecha(pago.fecha_pago)}</td>
            <td>${pago.metodo}</td>
          `;

          tbody.appendChild(tr);
        });
      });

      } catch (err) {
        console.error("Error cargando pagos:", err);
      }
    }

    // =====================================
    // ABRIR MODAL
    // =====================================
    btnAbrir.addEventListener("click", async () => {
      if (!alumnoSeleccionado) {
        alert("Seleccioná un alumno antes de agregar un cobro.");
        return;
      }

      await cargarMesesPendientes();
      modal.style.display = "block";
    });

    // BOTÓN CANCELAR
    document.getElementById("btnCancelar").addEventListener("click", () => {
        modal.style.display = "none";
        form.reset();
    });

    // Cerrar modal al hacer clic afuera
    window.addEventListener("click", function(e) {
        if (e.target === modal) {
            modal.style.display = "none";
            form.reset();
        }
    });


    // =====================================
    // CARGAR MESES DINÁMICOS
    // =====================================
    async function cargarMesesPendientes() {
      try {
        const url = `${API_BASE}/api/ctacte/pendientes/?alumno=${alumnoSeleccionado.id_alumno}`;
        const resp = await fetch(url);
        const data = await resp.json();

        contenedorMeses.innerHTML = `<h2>Meses</h2>`;

        // MESES POR AÑO
        for (const anio in data.meses) {
          const meses = data.meses[anio];

          let html = `
            <div class="year-group">
              <h3>${anio}</h3>
              <div class="months-grid">
          `;

          meses.forEach((m) => {

            const esInscripcion =
              m.descripcion.toLowerCase() === "inscripcion" ||
              m.id_mes == 1;

            // ❌ Si es inscripción pero NO es el año de ingreso → NO mostrar
            if (esInscripcion && parseInt(anio) !== data.anio_ingreso) {
              return;
            }

            html += `
              <div class="month" data-id_mes="${m.id_mes}" data-anio="${anio}">
                <span>${m.descripcion}</span>
              </div>
            `;
          });




          html += `</div></div>`;
          contenedorMeses.innerHTML += html;
        }

        // EVENTOS DE SELECCIÓN
        document.querySelectorAll(".month").forEach((m) => {
          m.addEventListener("click", () => {
            m.classList.toggle("selected");
            actualizarImporteAuto();
          });
        });
      } catch (err) {
        console.error("Error cargando meses pendientes:", err);
      }
    }

    // =====================================
    // IMPORTE AUTOMÁTICO SUMANDO MESES
    // =====================================
    async function actualizarImporteAuto() {
      try {
        const seleccionados = document.querySelectorAll(".month.selected");
        if (!seleccionados.length) {
          document.getElementById("importe").value = "";
          return;
        }

        let total = 0;

        for (const m of seleccionados) {
          const anio = parseInt(m.dataset.anio);
          const idMes = m.dataset.id_mes;

          if (idMes === "INSCRIPCION") continue;

          const fechaRef = `${anio}-${String(idMes).padStart(2, "0")}-01`;

          const url = `${API_BASE}/api/valores/vigente/?carrera=${carreraSeleccionadaId}&concepto=${CONCEPTO_CUOTA_ID}&fecha=${fechaRef}`;

          const resp = await fetch(url);

          if (!resp.ok) {
            console.warn("Sin valor vigente para:", fechaRef);
            continue;
          }

          const data = await resp.json();
          total += parseFloat(data.importe);
        }

        document.getElementById("importe").value = total.toFixed(2);
      } catch (err) {
        console.error("Error sumando importes:", err);
      }
    }

    // =====================================
    // REGISTRAR PAGO
    // =====================================
    if (form) {
      form.addEventListener("submit", async (e) => {
        e.preventDefault();

        const mesesMarcados = document.querySelectorAll(".month.selected");
        if (!mesesMarcados.length) {
          alert("Seleccioná al menos un mes.");
          return;
        }

        const metodo = metodoSelect.value;
        const importe = parseFloat(document.getElementById("importe").value);

        if (!metodo || !importe) {
          alert("Completá todos los campos.");
          return;
        }

        const meses = [];
        let anioUsado = null;

        mesesMarcados.forEach((m) => {
          const idMes = m.dataset.id_mes;
          if (idMes === "INSCRIPCION") {
            meses.push("INSCRIPCION");
            anioUsado = alumnoSeleccionado.anio_ingreso;
          } else {
            meses.push(parseInt(idMes));
            anioUsado = parseInt(m.dataset.anio);
          }
        });

        const payload = {
          id_alumno: alumnoSeleccionado.id_alumno,
          id_metodo_pago: parseInt(metodo),
          meses: meses.filter((x) => x !== "INSCRIPCION"),
          anio: anioUsado,
          importe_total: importe,
        };

        try {
          const resp = await fetch(`${API_BASE}/api/ctacte/registrar-pago/`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload),
          });

          const data = await resp.json();

          if (!resp.ok || data.error) {
            alert("Error: " + (data.error || "No se pudo registrar el pago."));
            return;
          }

          alert("Pago registrado correctamente.");

          modal.style.display = "none";
          form.reset();
          cargarPagos(alumnoSeleccionado.id_alumno);
        } catch (err) {
          console.error("Error registrando pago:", err);
          alert("Error al guardar el pago.");
        }
      });
    }
  });
})();
