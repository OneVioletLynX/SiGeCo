// --- Buscador + Carga dinámica de meses + Registrar Pago ---
(function () {
  const metaApi = document.querySelector('meta[name="api-base"]');
  const API_BASE =
    (window.API_BASE && String(window.API_BASE).trim()) ||
    (metaApi ? metaApi.content.trim() : "") ||
    "http://127.0.0.1:8000";

  let alumnoSeleccionado = null;
  let carreraSeleccionadaId = null;
  let pagoSeleccionado = null;

  const CONCEPTO_CUOTA_ID = 1;
  const CONCEPTO_INSCRIPCION_ID = 2;

  document.addEventListener("DOMContentLoaded", () => {

    function formatearFecha(fechaISO) {
      if (!fechaISO) return "";
      const f = new Date(fechaISO);
      return `${String(f.getDate()).padStart(2, "0")}/${String(f.getMonth() + 1).padStart(2, "0")}/${f.getFullYear()} ${String(f.getHours()).padStart(2, "0")}:${String(f.getMinutes()).padStart(2, "0")}`;
    }

    const buscador = document.getElementById("buscador");
    const sugerencias = document.getElementById("sugerencias");

    const modal = document.getElementById("altaModal");
    const btnAbrir = document.getElementById("btnAgregar");
    const metodoSelect = document.getElementById("metodo_pago");
    const campoComprobante = document.getElementById("campo-comprobante");
    const campoTarjeta = document.getElementById("campo-tarjeta");
    const form = document.getElementById("cobroForm");
    const contenedorMeses = document.querySelector(".meses-container");

    const btnEliminarPago = document.getElementById("btnEliminarPago");
    const btnImprimir = document.getElementById("btnImprimir");

    // 🔹 Siempre deshabilitados al inicio
    btnEliminarPago.classList.add("disabled");
    btnImprimir.classList.add("disabled");

    // ===========================
    // BOTÓN IMPRIMIR
    // ===========================
    btnImprimir.addEventListener("click", () => {
      if (!pagoSeleccionado) {
        alert("No hay un pago seleccionado para imprimir.");
        return;
      }
      window.open(`/cobros/comprobante/${pagoSeleccionado}/`, "_blank");
    });

    // ===========================
    // MÉTODO DE PAGO (mostrar campos)
    // ===========================
    metodoSelect.addEventListener("change", function () {
      campoComprobante.classList.add("hidden");
      campoTarjeta.classList.add("hidden");

      if (this.value === "2") campoComprobante.classList.remove("hidden");
      if (this.value === "3") campoTarjeta.classList.remove("hidden");
    });

    // ===========================
    // BUSCADOR ALUMNOS
    // ===========================
    buscador.addEventListener("input", () => {
      const q = buscador.value.trim();

      if (q.length === 0) {
        document.querySelector(".search-container").classList.remove("shifted");
      }

      if (q.length < 2) {
        sugerencias.innerHTML = "";
        sugerencias.style.display = "none";
        return;
      }

      buscarAlumnos(q);
    });

    async function buscarAlumnos(q) {
      try {
        const resp = await fetch(`${API_BASE}/api/alumnos/?search=${encodeURIComponent(q)}`);
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

      const btnAgregar = document.getElementById("btnAgregar");
      if (btnAgregar) btnAgregar.style.display = "flex";

      cargarPagos(alumno.id_alumno);
    }

    // ===========================
    // CARGAR PAGOS
    // ===========================
    async function cargarPagos(alumnoId) {
      try {
        const resp = await fetch(`${API_BASE}/api/pago/?alumno=${alumnoId}`);
        const pagos = await resp.json();
        const tbody = document.getElementById("tabla-cobros");
        const searchContainer = document.querySelector(".search-container");

        tbody.innerHTML = "";

        // 🔹 Reset de selección
        pagoSeleccionado = null;
        btnEliminarPago.classList.add("disabled");
        btnImprimir.classList.add("disabled");

        // ================================
        // 🔍 Calcular si realmente tiene pagos
        // ================================
        const totalDetalles = pagos.reduce((acc, pago) => {
          const detalles = pago.detalles || [];
          return acc + detalles.length;
        }, 0);

        const tienePagos = totalDetalles > 0;

        // ================================  
        // 🔹 Mostrar/Ocultar botones
        // ================================
        btnEliminarPago.style.display = tienePagos ? "flex" : "none";
        btnImprimir.style.display = tienePagos ? "flex" : "none";

        // ================================
        // 🧾 Dibujar tabla
        // ================================
        pagos.forEach((pago) => {
          const detalles = pago.detalles || [];
          detalles.forEach((det) => {
            const tr = document.createElement("tr");
            tr.dataset.pago = pago.id_pago;

            tr.innerHTML = `
              <td>${det.anio}</td>
              <td>${det.mes}</td>
              <td>$${parseFloat(det.importe).toFixed(2)}</td>
              <td>${formatearFecha(pago.fecha_pago)}</td>
              <td>${pago.metodo}</td>
            `;

            tbody.appendChild(tr);
          });
        });

        // ================================
        // 🎯 Eventos de selección
        // ================================
        document.querySelectorAll("#tabla-cobros tr").forEach((row) => {
          row.addEventListener("click", () => {
            const pagoId = row.dataset.pago;

            // Quitar selección anterior
            document.querySelectorAll("#tabla-cobros tr")
              .forEach(r => r.classList.remove("selected-pago"));

            // Marcar filas del pago
            document.querySelectorAll(`#tabla-cobros tr[data-pago='${pagoId}']`)
              .forEach(r => r.classList.add("selected-pago"));

            pagoSeleccionado = pagoId;

            // Habilitar acciones
            btnEliminarPago.classList.remove("disabled");
            btnImprimir.classList.remove("disabled");
          });
        });

      } catch (err) {
        console.error("Error cargando pagos:", err);
      }
    }

    // ===========================
    // ELIMINAR PAGO COMPLETO
    // ===========================
    if (btnEliminarPago) {
      btnEliminarPago.addEventListener("click", async () => {
        if (!pagoSeleccionado) {
          alert("Seleccioná un pago para eliminar.");
          return;
        }

        if (!confirm("¿Eliminar TODO el pago seleccionado?")) return;

        const resp = await fetch(`${API_BASE}/api/pago/${pagoSeleccionado}/`, {
          method: "DELETE",
        });

        if (resp.ok) {
          alert("Pago eliminado correctamente.");
          cargarPagos(alumnoSeleccionado.id_alumno);

          pagoSeleccionado = null;
          btnEliminarPago.classList.add("disabled");
          btnImprimir.classList.add("disabled");

        } else {
          alert("Error eliminando el pago.");
        }
      });
    }

    // ===========================
    // ABRIR MODAL
    // ===========================
    btnAbrir.addEventListener("click", async () => {
      if (!alumnoSeleccionado) {
        alert("Seleccioná un alumno primero.");
        return;
      }
      await cargarMesesPendientes();
      modal.style.display = "block";
    });

    // Cerrar modal
    document.getElementById("btnCancelar").addEventListener("click", () => {
      modal.style.display = "none";
      form.reset();
    });

    window.addEventListener("click", function (e) {
      if (e.target === modal) {
        modal.style.display = "none";
        form.reset();
      }
    });

    // ===========================
    // CARGAR MESES PENDIENTES
    // ===========================
    async function cargarMesesPendientes() {
      try {
        const resp = await fetch(`${API_BASE}/ctacte/pendientes/?alumno=${alumnoSeleccionado.id_alumno}`);
        const data = await resp.json();

        contenedorMeses.innerHTML = `<h2>Meses</h2>`;

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

            if (esInscripcion && parseInt(anio) !== data.anio_ingreso) return;

            html += `
              <div class="month" data-id_mes="${m.id_mes}" data-anio="${anio}">
                <span>${m.descripcion}</span>
              </div>
            `;
          });

          html += `</div></div>`;
          contenedorMeses.innerHTML += html;
        }

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

    // ===========================
    // SUMAR IMPORTES AUTOMÁTICAMENTE
    // ===========================
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

          const resp = await fetch(
            `${API_BASE}/api/valores/vigente/?carrera=${carreraSeleccionadaId}&concepto=${CONCEPTO_CUOTA_ID}&fecha=${fechaRef}`
          );

          if (!resp.ok) continue;

          const data = await resp.json();
          total += parseFloat(data.importe);
        }

        document.getElementById("importe").value = total.toFixed(2);

      } catch (err) {
        console.error("Error sumando importes:", err);
      }
    }

    // ===========================
    // REGISTRAR PAGO
    // ===========================
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

        mesesMarcados.forEach((m) => {
          const idMes = parseInt(m.dataset.id_mes);
          const anio = parseInt(m.dataset.anio);

          if (idMes === 0 || idMes === "INSCRIPCION") {
            meses.push({ mes: "INSCRIPCION", anio: alumnoSeleccionado.anio_ingreso });
          } else {
            meses.push({ mes: idMes, anio: anio });
          }
        });

        const payload = {
          id_alumno: alumnoSeleccionado.id_alumno,
          id_metodo_pago: parseInt(metodo),
          meses: meses,
          importe_total: importe,
        };

        try {
          const resp = await fetch(`${API_BASE}/ctacte/registrar-pago/`, {
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

          if (data.id_pago) {
            window.open(`/cobros/comprobante/${data.id_pago}/`, "_blank");
          }

        } catch (err) {
          console.error("Error registrando pago:", err);
          alert("Error al guardar el pago.");
        }
      });
    }
  });
})();
