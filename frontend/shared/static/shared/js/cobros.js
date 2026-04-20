// --- Buscador + Carga dinámica de meses + Registrar Pago ---
(function () {
  const metaApi = document.querySelector('meta[name="api-base"]');
  const API_BASE =
    (window.API_BASE && String(window.API_BASE).trim()) ||
    (metaApi ? metaApi.content.trim() : "") ||
    "http://127.0.0.1:8000";

  let alumnoSeleccionado    = null;
  let carreraSeleccionadaId = null;
  let pagoSeleccionado      = null;

  const CONCEPTO_CUOTA_ID       = 1;
  const CONCEPTO_INSCRIPCION_ID = 2;

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

  document.addEventListener("DOMContentLoaded", () => {

    if (!getToken()) { logout(); return; }

    const buscador         = document.getElementById("buscador");
    const sugerencias      = document.getElementById("sugerencias");
    const metodoSelect     = document.getElementById("metodo_pago");
    const campoComprobante = document.getElementById("campo-comprobante");
    const campoTarjeta     = document.getElementById("campo-tarjeta");
    const form             = document.getElementById("cobroForm");
    const contenedorMeses  = document.querySelector(".meses-container");
    const btnImprimir      = document.getElementById("btnImprimirPago");
    const btnEliminar      = document.getElementById("btnEliminarPago");

    let ultimoPagadoGlobal = null;

    // ===========================
    // BLOQUEO DE MESES
    // ===========================

    function recalcularBloqueos() {
      document.querySelectorAll(".month").forEach(m => m.classList.remove("bloqueado"));
      const seleccionados = document.querySelectorAll(".month.selected");

      if (seleccionados.length === 0) {
        const proximo = obtenerProximoMesPermitido();
        if (!proximo) return;
        document.querySelectorAll(".month").forEach(m => {
          if (m.classList.contains("pagado")) return;
          const anio = parseInt(m.dataset.anio);
          const mes  = parseInt(m.dataset.id_mes);
          if (anio !== proximo.anio || mes !== proximo.mes) m.classList.add("bloqueado");
        });
        return;
      }

      const valores = Array.from(seleccionados).map(m =>
        parseInt(m.dataset.anio) * 100 + parseInt(m.dataset.id_mes)
      );
      valores.sort((a, b) => b - a);

      const anioUlt = Math.floor(valores[0] / 100);
      const mesUlt  = valores[0] % 100;

      let siguienteAnio, siguienteMes;
      if (mesUlt === 1)       { siguienteAnio = anioUlt;     siguienteMes = 2; }
      else if (mesUlt === 11) { siguienteAnio = anioUlt + 1; siguienteMes = 2; }
      else                    { siguienteAnio = anioUlt;     siguienteMes = mesUlt + 1; }

      document.querySelectorAll(".month").forEach(m => {
        if (m.classList.contains("pagado"))   return;
        if (m.classList.contains("selected")) return;
        const anio = parseInt(m.dataset.anio);
        const mes  = parseInt(m.dataset.id_mes);
        if (anio !== siguienteAnio || mes !== siguienteMes) m.classList.add("bloqueado");
      });
    }

    function obtenerProximoMesPermitido() {
      if (!ultimoPagadoGlobal) return null;
      const { anio, mes } = ultimoPagadoGlobal;
      if (mes === 1)  return { anio: anio,     mes: 2 };
      if (mes === 11) return { anio: anio + 1, mes: 2 };
      return { anio: anio, mes: mes + 1 };
    }

    function seleccionConsecutivaValida() {
      const seleccionados = Array.from(document.querySelectorAll(".month.selected"));
      if (seleccionados.length <= 1) return true;

      const valores = seleccionados.map(m =>
        parseInt(m.dataset.anio) * 100 + parseInt(m.dataset.id_mes)
      );
      valores.sort((a, b) => a - b);

      for (let i = 1; i < valores.length; i++) {
        const anioAnt = Math.floor(valores[i - 1] / 100);
        const mesAnt  = valores[i - 1] % 100;
        const anioAct = Math.floor(valores[i] / 100);
        const mesAct  = valores[i] % 100;

        let expAnio, expMes;
        if (mesAnt === 1)       { expAnio = anioAnt;     expMes = 2; }
        else if (mesAnt === 11) { expAnio = anioAnt + 1; expMes = 2; }
        else                    { expAnio = anioAnt;     expMes = mesAnt + 1; }

        if (anioAct !== expAnio || mesAct !== expMes) return false;
      }
      return true;
    }

    // ===========================
    // IMPRIMIR
    // ===========================
    if (btnImprimir) {
      btnImprimir.addEventListener("click", () => {
        if (!pagoSeleccionado) return;
        window.open(`/cobros/comprobante/${pagoSeleccionado}/`, "_blank");
      });
    }

    // ===========================
    // MÉTODO DE PAGO
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
      if (q.length === 0) document.querySelector(".search-container")?.classList.remove("shifted");
      if (q.length < 2) { sugerencias.innerHTML = ""; sugerencias.style.display = "none"; return; }
      buscarAlumnos(q);
    });

    async function buscarAlumnos(q) {
      try {
        const resp = await authFetch(`${API_BASE}/api/alumnos/?search=${encodeURIComponent(q)}`);
        if (!resp) return;
        const data    = await resp.json();
        const alumnos = Array.isArray(data) ? data : (data.results || []);

        sugerencias.innerHTML = "";
        if (!alumnos.length) {
          sugerencias.innerHTML = "<div class='no-results'>Sin resultados</div>";
          sugerencias.style.display = "block";
          return;
        }

        alumnos.forEach(al => {
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

      document.querySelector(".toolbar")?.classList.add("cobros-activo");
      document.querySelector(".cobro-layout")?.classList.add("cobros-activo");

      const carreras = alumno.carreras || [];

      if (carreras.length === 0) {
        contenedorMeses.innerHTML = `<h2>Meses</h2><p style="color:#888; margin-top:1rem;">El alumno no tiene carreras activas.</p>`;
        return;
      }

      if (carreras.length === 1) {
        // Una sola carrera → cargar directo
        carreraSeleccionadaId = carreras[0].id_carrera;
        await cargarMesesPendientes();
      } else {
        // Varias carreras → mostrar selector
        mostrarSelectorCarreras(carreras);
      }
    }

    // ===========================
    // SELECTOR DE CARRERA
    // ===========================
    function mostrarSelectorCarreras(carreras) {
      carreraSeleccionadaId = null;
      ultimoPagadoGlobal    = null;

      let html = `
        <h2>Meses</h2>
        <div style="margin-bottom: 1.2rem;">
          <p style="font-size:0.9rem; color:#888; margin-bottom:0.8rem;">El alumno cursa varias carreras. Seleccioná una para ver sus cuotas:</p>
          <div style="display:flex; flex-direction:column; gap:0.6rem;">
      `;

      carreras.forEach(c => {
        const fondoClaro = aclararColor(c.color || "#1E3A8A", 150);
        html += `
          <button
            class="btn-seleccionar-carrera"
            data-id="${c.id_carrera}"
            style="
              display:flex; align-items:center; gap:0.8rem;
              background:${fondoClaro}; border:2px solid ${c.color || '#1E3A8A'};
              border-radius:10px; padding:0.7rem 1rem;
              cursor:pointer; text-align:left; width:100%;
              font-size:0.95rem; font-weight:600; color:${c.color || '#1E3A8A'};
              transition: all 0.15s ease;
            "
          >
            <span style="width:10px; height:10px; border-radius:50%; background:${c.color || '#1E3A8A'}; flex-shrink:0;"></span>
            ${c.descripcion}
            <span style="margin-left:auto; font-size:0.78rem; font-weight:400; opacity:0.7;">${c.estado}</span>
          </button>
        `;
      });

      html += `</div></div>`;
      contenedorMeses.innerHTML = html;

      document.querySelectorAll(".btn-seleccionar-carrera").forEach(btn => {
        btn.addEventListener("click", async () => {
          carreraSeleccionadaId = parseInt(btn.dataset.id);

          // Marcar seleccionada visualmente
          document.querySelectorAll(".btn-seleccionar-carrera").forEach(b => {
            b.style.opacity = "0.5";
          });
          btn.style.opacity = "1";
          btn.style.transform = "scale(1.02)";

          await cargarMesesPendientes();
        });
      });
    }

    function aclararColor(hex, factor) {
      hex = hex.replace("#", "");
      const r = Math.min(255, parseInt(hex.substring(0, 2), 16) + factor);
      const g = Math.min(255, parseInt(hex.substring(2, 4), 16) + factor);
      const b = Math.min(255, parseInt(hex.substring(4, 6), 16) + factor);
      return `rgb(${r},${g},${b})`;
    }

    // ===========================
    // CANCELAR
    // ===========================
    document.getElementById("btnCancelar").addEventListener("click", () => {
      form.reset();
      document.querySelectorAll(".month.selected").forEach(m => m.classList.remove("selected"));
      document.getElementById("importe").value = "";
    });

    // ===========================
    // CARGAR MESES PENDIENTES
    // ===========================
    async function cargarMesesPendientes() {
      try {
        const resp = await authFetch(`${API_BASE}/ctacte/pendientes/?alumno=${alumnoSeleccionado.id_alumno}`);
        if (!resp) return;
        const data = await resp.json();

        ultimoPagadoGlobal = data.ultimo_pagado;

        // Obtener nombre de la carrera seleccionada
        const carreraObj = (alumnoSeleccionado.carreras || []).find(c => c.id_carrera === carreraSeleccionadaId);
        const nombreCarrera = carreraObj ? carreraObj.descripcion : "";
        const colorCarrera  = carreraObj ? carreraObj.color : "#1E3A8A";

        // Si hay varias carreras, mostrar botón para volver al selector
        let headerHtml = `<h2>Meses</h2>`;
        if ((alumnoSeleccionado.carreras || []).length > 1) {
          headerHtml += `
            <div style="display:flex; align-items:center; gap:0.6rem; margin-bottom:1rem;">
              <button id="btnVolverCarreras" style="
                background:none; border:none; cursor:pointer;
                color:#888; font-size:0.85rem; display:flex; align-items:center; gap:0.3rem;
              ">
                ← Cambiar carrera
              </button>
              <span style="
                background:${aclararColor(colorCarrera, 150)};
                color:${colorCarrera};
                border:1px solid ${colorCarrera};
                border-radius:20px; padding:2px 10px;
                font-size:0.82rem; font-weight:600;
              ">${nombreCarrera}</span>
            </div>
          `;
        }

        contenedorMeses.innerHTML = headerHtml;

        // Filtrar meses por carrera seleccionada
        for (const anio in data.meses) {
          const meses = data.meses[anio].filter(m => m.carrera === carreraSeleccionadaId);
          if (!meses.length) continue;

          let html = `<div class="year-group"><h3>${anio}</h3><div class="months-grid">`;

          meses.forEach(m => {
            const esInscripcion = m.id_mes == 1;
            if (esInscripcion && parseInt(anio) !== data.anio_ingreso) return;

            const claseEstado = m.estado === "pagada"    ? "pagado"
                              : m.estado === "pendiente" ? "pendiente"
                              : "";

            const dataPago = m.pagado && m.id_pago ? `data-pago="${m.id_pago}"` : "";

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

        recalcularBloqueos();

        document.querySelectorAll(".month").forEach(mes => {
          mes.addEventListener("click", () => onClickMes(mes));
        });

        // Botón volver al selector de carreras
        const btnVolver = document.getElementById("btnVolverCarreras");
        if (btnVolver) {
          btnVolver.addEventListener("click", () => {
            mostrarSelectorCarreras(alumnoSeleccionado.carreras || []);
          });
        }

      } catch (err) {
        console.error("Error cargando meses pendientes:", err);
      }
    }

    // ===========================
    // CLICK EN MES
    // ===========================
    function onClickMes(mes) {
      const esPagado = mes.classList.contains("pagado");

      if (mes.classList.contains("bloqueado")) {
        mes.classList.add("vibrar");
        setTimeout(() => mes.classList.remove("vibrar"), 300);
        showAlert("Debes pagar los meses en orden consecutivo.", "warning");
        return;
      }

      if (!esPagado) {
        document.querySelectorAll(".month.selected-pago").forEach(m => m.classList.remove("selected-pago"));
        pagoSeleccionado = null;
        if (btnEliminar) btnEliminar.classList.add("disabled");
        if (btnImprimir) btnImprimir.classList.add("disabled");

        mes.classList.toggle("selected");

        if (!seleccionConsecutivaValida()) {
          mes.classList.toggle("selected");
          mes.classList.add("vibrar");
          setTimeout(() => mes.classList.remove("vibrar"), 300);
          showAlert("Solo podés seleccionar meses consecutivos.", "warning");
          return;
        }

        actualizarImporteAuto();
        recalcularBloqueos();
        return;
      }

      document.querySelectorAll(".month.selected").forEach(m => m.classList.remove("selected"));
      actualizarImporteAuto();
      recalcularBloqueos();

      const pagoId = mes.dataset.pago;
      if (!pagoId) return;

      const yaSeleccionado = mes.classList.contains("selected-pago");
      document.querySelectorAll(".month").forEach(m => m.classList.remove("selected-pago"));

      if (!yaSeleccionado) {
        document.querySelectorAll(`.month[data-pago='${pagoId}']`).forEach(m => m.classList.add("selected-pago"));
        pagoSeleccionado = pagoId;
        if (btnEliminar) btnEliminar.classList.remove("disabled");
        if (btnImprimir) btnImprimir.classList.remove("disabled");
      } else {
        pagoSeleccionado = null;
        if (btnEliminar) btnEliminar.classList.add("disabled");
        if (btnImprimir) btnImprimir.classList.add("disabled");
      }
    }

    // ===========================
    // ELIMINAR PAGO
    // ===========================
    if (btnEliminar) {
      btnEliminar.addEventListener("click", async () => {
        if (!pagoSeleccionado) return;
        if (!confirm("¿Eliminar el pago completo?")) return;

        const resp = await authFetch(`${API_BASE}/ctacte/pagos/${pagoSeleccionado}/`, { method: "DELETE" });

        if (resp && resp.ok) {
          pagoSeleccionado = null;
          btnEliminar.classList.add("disabled");
          if (btnImprimir) btnImprimir.classList.add("disabled");
          await cargarMesesPendientes();
        } else {
          alert("Error eliminando el pago.");
        }
      });
    }

    // ===========================
    // SUMAR IMPORTES
    // ===========================
    async function actualizarImporteAuto() {
      try {
        const seleccionados = document.querySelectorAll(".month.selected");
        if (!seleccionados.length) { document.getElementById("importe").value = ""; return; }

        let total = 0;

        for (const m of seleccionados) {
          const anio  = parseInt(m.dataset.anio);
          const idMes = parseInt(m.dataset.id_mes);

          const concepto = idMes === 1 ? CONCEPTO_INSCRIPCION_ID : CONCEPTO_CUOTA_ID;
          const mesRef   = idMes >= 3 ? idMes : 1;
          const fechaRef = `${anio}-${String(mesRef).padStart(2, "0")}-01`;

          const resp = await authFetch(
            `${API_BASE}/api/valores/vigente/?carrera=${carreraSeleccionadaId}&concepto=${concepto}&fecha=${fechaRef}`
          );
          if (!resp || !resp.ok) continue;

          const data = await resp.json();
          total += parseFloat(data.importe) || 0;
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
        if (!mesesMarcados.length) { showAlert("Seleccioná al menos un mes.", "warning"); return; }

        const metodo = metodoSelect.value;
        if (!metodo) { showAlert("Seleccioná un método de pago.", "warning"); return; }

        if (!carreraSeleccionadaId) { showAlert("Seleccioná una carrera primero.", "warning"); return; }

        const meses = [];

        for (const m of mesesMarcados) {
          const idMes = parseInt(m.dataset.id_mes);
          const anio  = parseInt(m.dataset.anio);

          const concepto = idMes === 1 ? CONCEPTO_INSCRIPCION_ID : CONCEPTO_CUOTA_ID;
          const mesRef   = idMes >= 3 ? idMes : 1;
          const fechaRef = `${anio}-${String(mesRef).padStart(2, "0")}-01`;

          let importeMes = 0;
          try {
            const r = await authFetch(
              `${API_BASE}/api/valores/vigente/?carrera=${carreraSeleccionadaId}&concepto=${concepto}&fecha=${fechaRef}`
            );
            if (r && r.ok) {
              const v = await r.json();
              importeMes = parseFloat(v.importe) || 0;
            }
          } catch (_) {}

          meses.push({
            carrera:  carreraSeleccionadaId,
            mes:      idMes,
            anio:     anio,
            concepto: concepto,
            importe:  importeMes,
          });
        }

        const importeTotal = meses.reduce((acc, m) => acc + m.importe, 0);

        if (importeTotal <= 0) {
          showAlert("No se pudo calcular el importe. Verificá los valores configurados.", "warning");
          return;
        }

        const payload = {
          id_alumno:      alumnoSeleccionado.id_alumno,
          id_metodo_pago: parseInt(metodo),
          meses,
          importe_total:  importeTotal,
        };

        try {
          const resp = await authFetch(`${API_BASE}/ctacte/registrar-pago/`, {
            method:  "POST",
            headers: { "Content-Type": "application/json" },
            body:    JSON.stringify(payload),
          });

          if (!resp) return;
          const data = await resp.json();

          if (!resp.ok || data.error) {
            showAlert("Error: " + (data.error || "No se pudo registrar el pago."), "error");
            return;
          }

          showAlert("Pago registrado correctamente.", "success");
          form.reset();
          await cargarMesesPendientes();

          if (data.id_pago) window.open(`/cobros/comprobante/${data.id_pago}/`, "_blank");

        } catch (err) {
          console.error("Error registrando pago:", err);
          showAlert("Error al guardar el pago.", "error");
        }
      });
    }
// ===========================
    // PRESELECCIÓN POR URL
    // ===========================
    const params    = new URLSearchParams(window.location.search);
    const alumnoId  = params.get("alumno");
    const carreraId = params.get("carrera");

    if (alumnoId) {
      authFetch(`${API_BASE}/api/alumnos/${alumnoId}/`).then(async resp => {
        if (!resp) return;
        const alumno = await resp.json();
        const carreras = alumno.carreras || [];

        // Llenar el buscador
        buscador.value = `${alumno.apellido}, ${alumno.nombre}`;
        alumnoSeleccionado = alumno;

        document.querySelector(".toolbar")?.classList.add("cobros-activo");
        document.querySelector(".cobro-layout")?.classList.add("cobros-activo");

        if (carreras.length === 0) return;

        if (carreras.length === 1 || !carreraId) {
          // Una sola carrera → cargar directo
          carreraSeleccionadaId = carreras[0].id_carrera;
          await cargarMesesPendientes();
        } else {
          // Varias carreras → mostrar selector y hacer click en la correcta
          mostrarSelectorCarreras(carreras);
          const carreraIdInt = parseInt(carreraId);
          setTimeout(() => {
            const btn = document.querySelector(
              `.btn-seleccionar-carrera[data-id="${carreraIdInt}"]`
            );
            if (btn) btn.click();
          }, 200);
        }
      });
    }
  });
})();