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

    const metodoSelect = document.getElementById("metodo_pago");
    const campoComprobante = document.getElementById("campo-comprobante");
    const campoTarjeta = document.getElementById("campo-tarjeta");
    const form = document.getElementById("cobroForm");
    const contenedorMeses = document.querySelector(".meses-container");
    let ultimoPagadoGlobal = null;
    const btnImprimir = document.getElementById("btnImprimirPago");

    function recalcularBloqueos() {

      document.querySelectorAll(".month").forEach(m => {
        m.classList.remove("bloqueado");
      });

      const seleccionados = document.querySelectorAll(".month.selected");

      if (seleccionados.length === 0) {
        const proximo = obtenerProximoMesPermitido();

        if (!proximo) return;

        document.querySelectorAll(".month").forEach(m => {

          if (m.classList.contains("pagado")) return;

          const anio = parseInt(m.dataset.anio);
          const mes = parseInt(m.dataset.id_mes);

          if (anio !== proximo.anio || mes !== proximo.mes) {
            m.classList.add("bloqueado");
          }
        });

        return;
      }

      // Si ya hay seleccionados → solo permitir el siguiente al último seleccionado
      const valores = Array.from(seleccionados).map(m => {
        return parseInt(m.dataset.anio) * 100 + parseInt(m.dataset.id_mes);
      });

      valores.sort((a, b) => b - a);

      const ultimo = valores[0];

      const anioUlt = Math.floor(ultimo / 100);
      const mesUlt = ultimo % 100;

      const fecha = new Date(anioUlt, mesUlt - 1);
      fecha.setMonth(fecha.getMonth() + 1);

      const siguienteAnio = fecha.getFullYear();
      const siguienteMes = fecha.getMonth() + 1;

      document.querySelectorAll(".month").forEach(m => {

        if (m.classList.contains("pagado")) return;
        if (m.classList.contains("selected")) return;

        const anio = parseInt(m.dataset.anio);
        const mes = parseInt(m.dataset.id_mes);

        if (anio !== siguienteAnio || mes !== siguienteMes) {
          m.classList.add("bloqueado");
        }
      });
    }

    function recalcularBloqueos() {

      document.querySelectorAll(".month").forEach(m => {
        m.classList.remove("bloqueado");
      });

      const seleccionados = document.querySelectorAll(".month.selected");

      if (seleccionados.length === 0) {

        const proximo = obtenerProximoMesPermitido();
        if (!proximo) return;

        document.querySelectorAll(".month").forEach(m => {

          if (m.classList.contains("pagado")) return;

          const anio = parseInt(m.dataset.anio);
          const mes = parseInt(m.dataset.id_mes);

          if (anio !== proximo.anio || mes !== proximo.mes) {
            m.classList.add("bloqueado");
          }
        });

        return;
      }

      const valores = Array.from(seleccionados).map(m => {
        return parseInt(m.dataset.anio) * 100 + parseInt(m.dataset.id_mes);
      });

      valores.sort((a, b) => b - a);

      const ultimo = valores[0];

      const anioUlt = Math.floor(ultimo / 100);
      const mesUlt = ultimo % 100;

      const fecha = new Date(anioUlt, mesUlt - 1);
      fecha.setMonth(fecha.getMonth() + 1);

      const siguienteAnio = fecha.getFullYear();
      const siguienteMes = fecha.getMonth() + 1;

      document.querySelectorAll(".month").forEach(m => {

        if (m.classList.contains("pagado")) return;
        if (m.classList.contains("selected")) return;

        const anio = parseInt(m.dataset.anio);
        const mes = parseInt(m.dataset.id_mes);

        if (anio !== siguienteAnio || mes !== siguienteMes) {
          m.classList.add("bloqueado");
        }
      });
    }
    
    if (btnImprimir) {
      btnImprimir.addEventListener("click", () => {

        if (!pagoSeleccionado) return;

        window.open(
          `/cobros/comprobante/${pagoSeleccionado}/`,
          "_blank"
        );

      });
    }

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
      // Activar layout cuando se selecciona alumno
      document.querySelector(".toolbar")?.classList.add("cobros-activo");
      document.querySelector(".cobro-layout")?.classList.add("cobros-activo");
      await cargarMesesPendientes(); // 👈 ahora esto es lo que corresponde
    }


    // Cerrar modal
    document.getElementById("btnCancelar").addEventListener("click", () => {
      form.reset();

      document.querySelectorAll(".month.selected")
        .forEach(m => m.classList.remove("selected"));

      document.getElementById("importe").value = "";
    });
    
    function obtenerProximoMesPermitido() {

      if (!ultimoPagadoGlobal) return null;

      const fechaUlt = new Date(
        ultimoPagadoGlobal.anio,
        ultimoPagadoGlobal.mes - 1
      );

      fechaUlt.setMonth(fechaUlt.getMonth() + 1);

      return {
        anio: fechaUlt.getFullYear(),
        mes: fechaUlt.getMonth() + 1
      };
    }
    // ===========================
    // CARGAR MESES PENDIENTES
    // ===========================
    async function cargarMesesPendientes() {
      try {
        const resp = await fetch(`${API_BASE}/ctacte/pendientes/?alumno=${alumnoSeleccionado.id_alumno}`);
        const data = await resp.json();
        ultimoPagadoGlobal = data.ultimo_pagado;
        recalcularBloqueos();
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
              m.descripcion.toLowerCase() === "inscripción" ||
              m.id_mes == 1;

            if (esInscripcion && parseInt(anio) !== data.anio_ingreso) return;

            let claseEstado = "";

            if (m.estado === "pagado") {
              claseEstado = "pagado";
            }

            if (m.estado === "pendiente") {
              claseEstado = "pendiente";
            }
            const dataPago = m.pagado ? `data-pago="${m.id_pago}"` : "";

            html += `
              <div class="month ${claseEstado}"
                  data-id_mes="${m.id_mes}"
                  data-anio="${anio}"
                  ${dataPago}>
                <span>${m.descripcion}</span>
              </div>
            `;
          });

          html += `</div></div>`;
          contenedorMeses.innerHTML += html;
        }
        const proximo = obtenerProximoMesPermitido();

        if (proximo) {

          document.querySelectorAll(".month").forEach(m => {

            if (m.classList.contains("pagado")) return;

            const anio = parseInt(m.dataset.anio);
            const mes = parseInt(m.dataset.id_mes);

            if (anio !== proximo.anio || mes !== proximo.mes) {
              m.classList.add("bloqueado");
            }
          });
        }
        document.querySelectorAll(".month").forEach((mes) => {

        mes.addEventListener("click", () => {

          const esPagado = mes.classList.contains("pagado");

          // 🔒 Si está bloqueado → vibrar y salir
          if (mes.classList.contains("bloqueado")) {

            mes.classList.add("vibrar");

            setTimeout(() => {
              mes.classList.remove("vibrar");
            }, 300);

            showAlert("Debes pagar los meses en orden consecutivo.", "warning");

            return;
          }
          // 🔹 Si clickea un mes NO pagado
          if (!esPagado) {

            // Limpiar selección de pagos existentes
            document.querySelectorAll(".month.selected-pago")
              .forEach(m => m.classList.remove("selected-pago"));

            pagoSeleccionado = null;

            if (btnEliminar) btnEliminar.classList.add("disabled");
            if (btnImprimir) btnImprimir.classList.add("disabled");

            mes.classList.toggle("selected");

            // 🔥 habilitar siguiente mes
            const anio = parseInt(mes.dataset.anio);
            const mesNum = parseInt(mes.dataset.id_mes);

            const fecha = new Date(anio, mesNum - 1);
            fecha.setMonth(fecha.getMonth() + 1);

            const siguienteAnio = fecha.getFullYear();
            const siguienteMes = fecha.getMonth() + 1;

            document.querySelectorAll(".month.bloqueado").forEach(m => {
              if (
                parseInt(m.dataset.anio) === siguienteAnio &&
                parseInt(m.dataset.id_mes) === siguienteMes
              ) {
                m.classList.remove("bloqueado");
              }
            });

            if (!seleccionConsecutivaValida()) {

              mes.classList.toggle("selected"); // revertir

              // 🔥 efecto vibración
              mes.classList.add("vibrar");

              setTimeout(() => {
                mes.classList.remove("vibrar");
              }, 300);

              showAlert("Solo podés seleccionar meses consecutivos.", "warning");

              return;
            }

            actualizarImporteAuto();
            recalcularBloqueos()
            return;
          }

          function seleccionConsecutivaValida() {

          const seleccionados = Array.from(
            document.querySelectorAll(".month.selected")
          );

          if (seleccionados.length <= 1) return true;

          // Convertir a números tipo YYYYMM
          const valores = seleccionados.map(m => {
            const anio = parseInt(m.dataset.anio);
            const mes = parseInt(m.dataset.id_mes);
            return anio * 100 + mes;
          });

          valores.sort((a, b) => a - b);

          for (let i = 1; i < valores.length; i++) {

            const anterior = valores[i - 1];
            const actual = valores[i];

            const anioAnt = Math.floor(anterior / 100);
            const mesAnt = anterior % 100;

            const anioAct = Math.floor(actual / 100);
            const mesAct = actual % 100;

            const fechaAnt = new Date(anioAnt, mesAnt - 1);
            const fechaAct = new Date(anioAct, mesAct - 1);

            const diferenciaMeses =
              (fechaAct.getFullYear() - fechaAnt.getFullYear()) * 12 +
              (fechaAct.getMonth() - fechaAnt.getMonth());

            if (diferenciaMeses !== 1) {
              return false;
            }
          }

          return true;
        }
          // 🔹 Si clickea un mes pagado

          // Limpiar selección de meses nuevos
          document.querySelectorAll(".month.selected")
            .forEach(m => m.classList.remove("selected"));

          actualizarImporteAuto(); // limpia importe
          recalcularBloqueos(); 
          const pagoId = mes.dataset.pago;
          if (!pagoId) return;

          const yaSeleccionado = mes.classList.contains("selected-pago");

          // Limpiar selección anterior
          document.querySelectorAll(".month")
            .forEach(m => m.classList.remove("selected-pago"));

          if (!yaSeleccionado) {

            document.querySelectorAll(`.month[data-pago='${pagoId}']`)
              .forEach(m => m.classList.add("selected-pago"));

            pagoSeleccionado = pagoId;

            if (btnEliminar) btnEliminar.classList.remove("disabled");
            if (btnImprimir) btnImprimir.classList.remove("disabled");

          } else {

            pagoSeleccionado = null;

            if (btnEliminar) btnEliminar.classList.add("disabled");
            if (btnImprimir) btnImprimir.classList.add("disabled");
          }

        });

        });

      } catch (err) {
        console.error("Error cargando meses pendientes:", err);
      }
    }

    const btnEliminar = document.getElementById("btnEliminarPago");

    if (btnEliminar) {
      btnEliminar.addEventListener("click", async () => {

        if (!pagoSeleccionado) return;
        if (!confirm("¿Eliminar el pago completo?")) return;

        const resp = await fetch(`${API_BASE}/api/pago/${pagoSeleccionado}/`, {
          method: "DELETE"
        });

        if (resp.ok) {
          pagoSeleccionado = null;
          btnEliminar.classList.add("disabled");

          if (btnImprimir) {
            btnImprimir.classList.add("disabled");
          }

          await cargarMesesPendientes();
        } else {
          alert("Error eliminando el pago.");
        }

      });
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
          showAlert("Seleccioná al menos un mes.", "warning");

          return;
        }

        const metodo = metodoSelect.value;
        const importe = parseFloat(document.getElementById("importe").value);

        if (!metodo || !importe) {
          showAlert("Completá todos los campos.", "warning");

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
            showAlert("Error: " + (data.error || "No se pudo registrar el pago."), "error");

            return;
          }

          showAlert("Pago registrado correctamente.", "success");

          form.reset();
          await cargarMesesPendientes();

          if (data.id_pago) {
            window.open(`/cobros/comprobante/${data.id_pago}/`, "_blank");
          }

        } catch (err) {
          console.error("Error registrando pago:", err);
          showAlert("Error al guardar el pago.", "error");

        }
      });
    }
  });
})();
