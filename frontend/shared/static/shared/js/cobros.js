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

  const AVATAR_COLORS = [
    "#4f46e5","#0891b2","#059669","#d97706","#dc2626",
    "#7c3aed","#db2777","#0284c7","#16a34a","#ca8a04"
  ];

  function avatarColor(name) {
    let h = 0;
    for (let i = 0; i < name.length; i++) h = (h * 31 + name.charCodeAt(i)) & 0xffff;
    return AVATAR_COLORS[h % AVATAR_COLORS.length];
  }

  function getInitials(nombre, apellido) {
    const n = (nombre || "").trim();
    const a = (apellido || "").trim();
    return ((a[0] || "") + (n[0] || "")).toUpperCase() || "?";
  }

  const METODO_COLORES = {
    "efectivo":      { bg: "#dcfce7", color: "#166534" },
    "transferencia": { bg: "#dbeafe", color: "#1e40af" },
    "débito":        { bg: "#fef9c3", color: "#854d0e" },
    "debito":        { bg: "#fef9c3", color: "#854d0e" },
    "tarjeta":       { bg: "#fce7f3", color: "#9d174d" },
    "crédito":       { bg: "#fce7f3", color: "#9d174d" },
    "credito":       { bg: "#fce7f3", color: "#9d174d" },
    "cheque":        { bg: "#d1fae5", color: "#065f46" },
  };

  function metodoChip(metodo) {
    if (!metodo) return "";
    const key = metodo.toLowerCase();
    let style = { bg: "#ede9fe", color: "#5b21b6" };
    for (const [k, v] of Object.entries(METODO_COLORES)) {
      if (key.includes(k)) { style = v; break; }
    }
    return `<span class="mes-metodo-chip" style="background:${style.bg};color:${style.color};">${metodo}</span>`;
  }

  const CONCEPTO_CUOTA_ID = 1;
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

    const buscador = document.getElementById("buscador");
    const sugerencias = document.getElementById("sugerencias");
    const metodoSelect = document.getElementById("metodo_pago");
    const campoComprobante = document.getElementById("campo-comprobante");
    const campoTarjeta = document.getElementById("campo-tarjeta");
    const form = document.getElementById("cobroForm");
    const contenedorMeses = document.querySelector(".meses-container");
    const btnImprimir = document.getElementById("btnImprimirPago");
    const btnEliminar = document.getElementById("btnEliminarPago");

    let ultimoPagadoGlobal = null;

    // ===========================
    // ALUMNO CARD
    // ===========================

    function renderAlumnoCard(alumno) {
      const card = document.getElementById("alumnoCard");
      if (!card) return;
      const color = avatarColor(`${alumno.nombre} ${alumno.apellido}`);
      const initials = getInitials(alumno.nombre, alumno.apellido);
      const dni = alumno.dni ? `DNI ${String(alumno.dni).replace(/\B(?=(\d{3})+(?!\d))/g, ".")}` : "";
      card.innerHTML = `
        <div class="alumno-avatar-cobro" style="background:${color};">${initials}</div>
        <div class="alumno-info-cobro">
          <span class="alumno-nombre-cobro">${alumno.apellido}, ${alumno.nombre}</span>
          <span class="alumno-meta-cobro">${dni}</span>
        </div>
        <button type="button" id="btnCambiarAlumno" class="btn-cambiar-alumno">
          <span class="material-icons">close</span>
          Cambiar
        </button>
      `;
      card.style.display = "flex";

      document.getElementById("btnCambiarAlumno")?.addEventListener("click", limpiarSeleccion);
    }

    function limpiarSeleccion() {
      alumnoSeleccionado = null;
      carreraSeleccionadaId = null;
      pagoSeleccionado = null;
      buscador.value = "";
      const card = document.getElementById("alumnoCard");
      if (card) card.style.display = "none";
      contenedorMeses.innerHTML = `
        <h2>Meses</h2>
        <div class="meses-placeholder">
          <span class="material-icons">calendar_month</span>
          <span>Buscá un alumno para ver sus cuotas</span>
        </div>
      `;
      document.querySelector(".cobro-layout")?.classList.remove("cobros-activo");
      if (btnEliminar) btnEliminar.classList.add("disabled");
      if (btnImprimir) btnImprimir.classList.add("disabled");
      form.reset();
    }

    // ===========================
    // BLOQUEO DE MESES
    // ===========================

    function recalcularBloqueos() {
      document.querySelectorAll(".month")
      document.querySelectorAll(".month").forEach(m => m.classList.remove("bloqueado"));
      const seleccionados = document.querySelectorAll(".month.selected");

      const todosPendientes = Array.from(document.querySelectorAll(".month:not(.pagado)"))
        .map(m => parseInt(m.dataset.anio) * 100 + parseInt(m.dataset.id_mes))
        .sort((a, b) => a - b);

      if (!todosPendientes.length) return;

      if (seleccionados.length === 0) {
        if (!ultimoPagadoGlobal) {
          const primero = todosPendientes[0];
          document.querySelectorAll(".month:not(.pagado)").forEach(m => {
            const val = parseInt(m.dataset.anio) * 100 + parseInt(m.dataset.id_mes);
            if (val !== primero) m.classList.add("bloqueado");
          });
          return;
        }

        const { anio, mes } = ultimoPagadoGlobal;
        let sigAnio, sigMes;
        if (mes === 1)       { sigAnio = anio;     sigMes = 2; }
        else if (mes === 11) { sigAnio = anio + 1; sigMes = 2; }
        else                 { sigAnio = anio;     sigMes = mes + 1; }

        const sigVal = sigAnio * 100 + sigMes;
        const habilitado = todosPendientes.includes(sigVal) ? sigVal : todosPendientes[0];


        document.querySelectorAll(".month:not(.pagado)").forEach(m => {
          const val = parseInt(m.dataset.anio) * 100 + parseInt(m.dataset.id_mes);
          if (val !== habilitado) m.classList.add("bloqueado");
        });
        return;
      }

      // Con meses seleccionados
      const valores = Array.from(seleccionados)
        .map(m => parseInt(m.dataset.anio) * 100 + parseInt(m.dataset.id_mes))
        .sort((a, b) => b - a);

      const anioUlt = Math.floor(valores[0] / 100);
      const mesUlt  = valores[0] % 100;

      let sigAnio, sigMes;
      if (mesUlt === 1)       { sigAnio = anioUlt;     sigMes = 2; }
      else if (mesUlt === 11) { sigAnio = anioUlt + 1; sigMes = 2; }
      else                    { sigAnio = anioUlt;     sigMes = mesUlt + 1; }

      const sigVal = sigAnio * 100 + sigMes;

      const pendientesNoSel = Array.from(document.querySelectorAll(".month:not(.pagado):not(.selected)"))
        .map(m => parseInt(m.dataset.anio) * 100 + parseInt(m.dataset.id_mes))
        .sort((a, b) => a - b);

      const habilitado = pendientesNoSel.includes(sigVal) ? sigVal : (pendientesNoSel[0] || null);

    document.querySelectorAll(".month:not(.pagado)").forEach(m => {
      const val = parseInt(m.dataset.anio) * 100 + parseInt(m.dataset.id_mes);
      if (val !== habilitado) m.classList.add("bloqueado");
    });
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
        const mesAnt = valores[i - 1] % 100;
        const anioAct = Math.floor(valores[i] / 100);
        const mesAct = valores[i] % 100;

        let expAnio, expMes;
        if (mesAnt === 1) { expAnio = anioAnt; expMes = 2; }
        else if (mesAnt === 11) { expAnio = anioAnt + 1; expMes = 2; }
        else { expAnio = anioAnt; expMes = mesAnt + 1; }

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
        const resp = await authFetch(`${API_BASE}/api/alumnos/?search=${encodeURIComponent(q)}&estado=1`);
        if (!resp) return;
        const data = await resp.json();
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

      renderAlumnoCard(alumno);
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
      ultimoPagadoGlobal = null;

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
      setTimeout(() => recalcularBloqueos(), 0);
    });

    // ===========================
    // CARGAR MESES PENDIENTES
    // ===========================
    async function cargarMesesPendientes() {
      contenedorMeses.innerHTML = `
        <h2>Meses</h2>
        <div class="meses-loading">
          <span class="material-icons rotating">refresh</span>
          Cargando cuotas...
        </div>
      `;
      try {
        const resp = await authFetch(`${API_BASE}/ctacte/pendientes/?alumno=${alumnoSeleccionado.id_alumno}`);
        if (!resp) return;
        const data = await resp.json();

        ultimoPagadoGlobal = data.ultimo_pagado;

        // Obtener nombre de la carrera seleccionada
        const carreraObj = (alumnoSeleccionado.carreras || []).find(c => c.id_carrera === carreraSeleccionadaId);
        const nombreCarrera = carreraObj ? carreraObj.descripcion : "";
        const colorCarrera = carreraObj ? carreraObj.color : "#1E3A8A";

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

        const aniosOrdenados = Object.keys(data.meses).sort((a, b) => b - a);
        const anioActual = new Date().getFullYear();

        let tableHtml = `<table class="meses-table">
          <thead><tr>
            <th style="width:48px;"></th>
            <th>Mes</th>
            <th>Método</th>
            <th>Importe</th>
            <th>Fecha</th>
          </tr></thead>
          <tbody>`;

        for (const anio of aniosOrdenados) {
          const meses = data.meses[anio].filter(m => m.carrera === carreraSeleccionadaId)
            .filter(m => !(m.id_mes == 1 && parseInt(anio) !== data.anio_ingreso));

          if (!meses.length) continue;

          const totalPagados    = meses.filter(m => m.estado === "pagada").length;
          const totalPendientes = meses.filter(m => m.estado === "pendiente").length;
          const summaryParts = [];
          if (totalPagados)    summaryParts.push(`${totalPagados} pagado${totalPagados > 1 ? "s" : ""}`);
          if (totalPendientes) summaryParts.push(`${totalPendientes} pendiente${totalPendientes > 1 ? "s" : ""}`);

          const collapsed = parseInt(anio) < anioActual && totalPagados === meses.length;

          tableHtml += `
            <tr class="year-row${collapsed ? " year-row-collapsed" : ""}" data-anio="${anio}">
              <td colspan="5" class="year-row-cell">
                <span class="material-icons year-chevron">expand_more</span>
                <strong>${anio}</strong>
                ${summaryParts.length ? `<span class="year-summary">· ${summaryParts.join(" · ")}</span>` : ""}
              </td>
            </tr>
          `;

          meses.forEach(m => {
            const claseEstado = m.estado === "pagada" ? "pagado"
              : m.estado === "pendiente" ? "pendiente" : "";
            const dataPago = m.id_pago ? `data-pago="${m.id_pago}"` : "";
            const checkIcon = m.estado === "pagada" ? "check_box" : "check_box_outline_blank";

            let metodoCell = "";
            let importeCell = "";
            let fechaCell = "";

            if (m.estado === "pagada" && m.fecha_pago) {
              metodoCell  = metodoChip(m.metodo);
              importeCell = m.importe
                ? `$${parseFloat(m.importe).toLocaleString("es-AR", { minimumFractionDigits: 0 })}`
                : "—";
              fechaCell = m.fecha_pago;
            } else if (m.estado === "pendiente") {
              metodoCell = `<span class="mes-estado-tag pendiente">Pendiente</span>`;
            }

            tableHtml += `
              <tr class="month ${claseEstado}${collapsed ? " year-hidden" : ""}"
                  data-id_mes="${m.id_mes}"
                  data-anio="${anio}"
                  ${dataPago}>
                <td style="padding-right:0; width:48px;">
                  <span class="material-icons mes-checkbox-icon">${checkIcon}</span>
                </td>
                <td class="mes-nombre-col">${m.descripcion}</td>
                <td>${metodoCell}</td>
                <td><span class="mes-importe-col">${importeCell}</span></td>
                <td><span class="mes-fecha-col">${fechaCell}</span></td>
              </tr>
            `;
          });
        }

        tableHtml += `</tbody></table>`;
        contenedorMeses.innerHTML += tableHtml;

        setTimeout(() => recalcularBloqueos(), 0);

        document.querySelectorAll(".month").forEach(mes => {
          mes.addEventListener("click", () => onClickMes(mes));
        });

        // Toggle colapso por año
        document.querySelectorAll(".year-row").forEach(row => {
          row.addEventListener("click", (e) => {
            e.stopPropagation();
            const anio = row.dataset.anio;
            row.classList.toggle("year-row-collapsed");
            document.querySelectorAll(`.month[data-anio="${anio}"]`).forEach(m => {
              m.classList.toggle("year-hidden");
            });
          });
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
    function actualizarCheckIcon(mes) {
      const icon = mes.querySelector(".mes-checkbox-icon");
      if (!icon) return;
      const esPagado = mes.classList.contains("pagado");
      if (esPagado) {
        icon.textContent = "check_box";
      } else {
        icon.textContent = mes.classList.contains("selected") ? "check_box" : "check_box_outline_blank";
      }
    }

    function onClickMes(mes) {
      const esPagado = mes.classList.contains("pagado");

      if (mes.classList.contains("bloqueado")) {
        console.log("bloqueado");
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
        actualizarCheckIcon(mes);

        if (!seleccionConsecutivaValida()) {
          mes.classList.toggle("selected");
          actualizarCheckIcon(mes);
          mes.classList.add("vibrar");
          setTimeout(() => mes.classList.remove("vibrar"), 300);
          showAlert("Solo podés seleccionar meses consecutivos.", "warning");
          return;
        }

        actualizarImporteAuto();
        setTimeout(() => recalcularBloqueos(), 0);

        return;
      }

      document.querySelectorAll(".month.selected").forEach(m => {
        m.classList.remove("selected");
        actualizarCheckIcon(m);
      });
      actualizarImporteAuto();
      setTimeout(() => recalcularBloqueos(), 0);

      const pagoId = mes.dataset.pago;
      if (!pagoId) return;

      const yaSeleccionado = mes.classList.contains("selected-pago");
      document.querySelectorAll(".month").forEach(m => m.classList.remove("selected-pago"));

      if (!yaSeleccionado) {
        document.querySelectorAll(`.month[data-pago='${pagoId}']`).forEach(m => {
          m.classList.add("selected-pago");
        });
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
          const anio = parseInt(m.dataset.anio);
          const idMes = parseInt(m.dataset.id_mes);

          const concepto = idMes === 1 ? CONCEPTO_INSCRIPCION_ID : CONCEPTO_CUOTA_ID;
          const mesRef = idMes >= 3 ? idMes : 1;
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
          const anio = parseInt(m.dataset.anio);

          const concepto = idMes === 1 ? CONCEPTO_INSCRIPCION_ID : CONCEPTO_CUOTA_ID;
          const mesRef = idMes >= 3 ? idMes : 1;
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
          } catch (_) { }

          meses.push({
            carrera: carreraSeleccionadaId,
            mes: idMes,
            anio: anio,
            concepto: concepto,
            importe: importeMes,
          });
        }

        const importeTotal = meses.reduce((acc, m) => acc + m.importe, 0);

        if (importeTotal <= 0) {
          showAlert("No se pudo calcular el importe. Verificá los valores configurados.", "warning");
          return;
        }

        const payload = {
          id_alumno: alumnoSeleccionado.id_alumno,
          id_metodo_pago: parseInt(metodo),
          meses,
          importe_total: importeTotal,
        };

        try {
          const resp = await authFetch(`${API_BASE}/ctacte/registrar-pago/`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload),
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
    const params = new URLSearchParams(window.location.search);
    const alumnoId = params.get("alumno");
    const carreraId = params.get("carrera");

    if (alumnoId) {
      authFetch(`${API_BASE}/api/alumnos/${alumnoId}/`).then(async resp => {
        if (!resp) return;
        const alumno = await resp.json();
        const carreras = alumno.carreras || [];

        // Llenar el buscador
        buscador.value = `${alumno.apellido}, ${alumno.nombre}`;
        alumnoSeleccionado = alumno;

        renderAlumnoCard(alumno);
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