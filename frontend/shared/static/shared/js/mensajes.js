// ==========================================
// CONFIGURACIÓN & HELPERS
// ==========================================

// Detectamos la base del backend (como en cobros.js / alumnos.js)
const metaApi = document.querySelector('meta[name="api-base"]');
const BASE_API =
  (window.API_BASE && String(window.API_BASE).trim()) ||
  (metaApi ? metaApi.content.trim() : "") ||
  "http://127.0.0.1:8000";

// Endpoints reales del backend
const API_BASE = `${BASE_API}/mensajes/api/`;
const SEARCH_ALUMNOS = `${BASE_API}/api/alumnos/?search=`;
const SEARCH_CARRERAS = `${BASE_API}/api/carreras/?search=`;

function getCookie(name) {
    const v = document.cookie.split('; ').find(row => row.startsWith(name + '='));
    return v ? decodeURIComponent(v.split('=')[1]) : null;
}
const csrftoken = getCookie('csrftoken');

function toDatetimeLocal(isoString) {
    if (!isoString) return '';
    const date = new Date(isoString);
    date.setMinutes(date.getMinutes() - date.getTimezoneOffset());
    return date.toISOString().slice(0, 16);
}

function formatDate(iso) {
    if (!iso) return '';
    const d = new Date(iso);
    return isNaN(d) ? iso : d.toLocaleDateString('es-AR', { day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit' });
}

function escapeHtml(text) {
    if (!text) return "";
    return String(text).replace(/[&<>"']/g, m => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#039;' })[m]);
}

// NOTIFICACIONES Y CONFIRMACIONES
function showToast(msg, type = 'success') {
    const container = document.getElementById('toast-container');
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.innerHTML = `<span>${msg}</span>`;
    container.appendChild(toast);
    setTimeout(() => toast.remove(), 3500);
}

function showConfirm(title, msg, onConfirm) {
    const modal = document.getElementById('confirm-modal');
    const titleEl = document.getElementById('confirm-title');
    const msgEl = document.getElementById('confirm-msg');
    const btnOk = document.getElementById('confirm-btn-ok');
    const btnCancel = document.getElementById('confirm-btn-cancel');

    titleEl.textContent = title;
    msgEl.textContent = msg;
    modal.style.display = 'flex';

    const newBtnOk = btnOk.cloneNode(true);
    btnOk.parentNode.replaceChild(newBtnOk, btnOk);
    const newBtnCancel = btnCancel.cloneNode(true);
    btnCancel.parentNode.replaceChild(newBtnCancel, btnCancel);

    newBtnOk.addEventListener('click', () => {
        modal.style.display = 'none';
        if (onConfirm) onConfirm();
    });

    newBtnCancel.addEventListener('click', () => {
        modal.style.display = 'none';
    });
}

// ==========================================
// LÓGICA WHATSAPP
// ==========================================
function abrirWhatsApp(telefono, mensaje) {
    if (!telefono || telefono == 0) return;
    let t = String(telefono).replace(/\D/g, '');
    if (!t.startsWith('54')) t = '549' + t;
    const url = `https://wa.me/${t}?text=${encodeURIComponent(mensaje)}`;
    window.open(url, '_blank');
}

// ==========================================
// ESTADO Y MODOS
// ==========================================
let appState = { mode: 'normal', page: 1, filter: '', search: '' };
const btnEdit = document.getElementById('btn-toggle-edit');
const btnDel = document.getElementById('btn-toggle-delete');
const body = document.body;

function setMode(newMode) {
    btnEdit.classList.remove('active-edit');
    btnDel.classList.remove('active-delete');
    body.classList.remove('mode-edit', 'mode-delete');

    if (appState.mode === newMode) {
        appState.mode = 'normal';
    } else {
        appState.mode = newMode;
        if (newMode === 'edit') {
            btnEdit.classList.add('active-edit');
            body.classList.add('mode-edit');
            showToast('Modo Edición: Toca un mensaje para editar', 'success');
        }
        if (newMode === 'delete') {
            btnDel.classList.add('active-delete');
            body.classList.add('mode-delete');
            showToast('Modo Eliminación: Toca para borrar', 'error');
        }
    }
}

btnEdit.addEventListener('click', () => setMode('edit'));
btnDel.addEventListener('click', () => setMode('delete'));

// ==========================================
// AUTOCOMPLETE
// ==========================================
function initAutocomplete(opts) {
    const input = document.getElementById(opts.inputId);
    const suggBox = document.getElementById(opts.suggId);
    const chipBox = document.getElementById(opts.chipId);
    let selected = [];
    let timer;

    const render = () => {
        chipBox.innerHTML = '';
        selected.forEach((item, idx) => {
            const chip = document.createElement('div');
            chip.className = 'chip';
            chip.innerHTML = `${item.name} <button type="button" class="chip-remove">×</button>`;
            chip.querySelector('button').onclick = () => { selected.splice(idx, 1); render(); };
            chipBox.appendChild(chip);
        });
    };

    input.addEventListener('input', (e) => {
        clearTimeout(timer);
        const q = e.target.value.trim();
        if (!q) { suggBox.style.display = 'none'; return; }
        timer = setTimeout(async () => {
            try {
                const res = await fetch(opts.url + encodeURIComponent(q));
                const data = await res.json();
                const items = Array.isArray(data) ? data : (data.results || []);
                suggBox.innerHTML = '';
                if (!items.length) {
                    suggBox.innerHTML = '<div class="suggestion-item" style="color:#999">Sin resultados</div>';
                } else {
                    items.slice(0, 6).forEach(i => {
                        const id = i[opts.idField];
                        const name = opts.formatName(i);
                        const div = document.createElement('div');
                        div.className = 'suggestion-item';
                        div.textContent = name;
                        div.onclick = () => {
                            if (!selected.some(s => String(s.id) === String(id))) { selected.push({ id, name }); render(); }
                            input.value = ''; suggBox.style.display = 'none';
                        };
                        suggBox.appendChild(div);
                    });
                }
                suggBox.style.display = 'block';
            } catch (e) { console.error(e); }
        }, 300);
    });

    document.addEventListener('click', e => { if (!input.contains(e.target)) suggBox.style.display = 'none'; });

    return {
        getIds: () => selected.map(s => s.id),
        set: (items) => { selected = items || []; render(); },
        clear: () => { selected = []; render(); input.value = ''; suggBox.style.display = 'none'; }
    };
}

const acAlumnos = initAutocomplete({
    inputId: 'input-alumnos', suggId: 'sugg-alumnos', chipId: 'chips-alumnos',
    url: SEARCH_ALUMNOS, idField: 'id_alumno', formatName: i => `${i.apellido}, ${i.nombre}`
});
const acCarreras = initAutocomplete({
    inputId: 'input-carreras', suggId: 'sugg-carreras', chipId: 'chips-carreras',
    url: SEARCH_CARRERAS, idField: 'id_carrera', formatName: i => i.descripcion
});

// ==========================================
// CRUD & FORMULARIO
// ==========================================
const form = document.getElementById('mensaje-form');
const containerFecha = document.getElementById('container-fecha');
const containerTitulo = document.getElementById('container-titulo');
const inputFecha = document.getElementById('fecha_envio');
const inputTitulo = document.getElementById('titulo');
const inputDesc = document.getElementById('descripcion');
const selectTipo = document.getElementById('tipo_envio');
let isScheduled = false;

// Modales
function closeTipoModal() { document.getElementById('tipo-modal').style.display = 'none'; }
function closeMainModal() { document.getElementById('main-modal').style.display = 'none'; }

document.getElementById('fab-btn').addEventListener('click', () => { document.getElementById('tipo-modal').style.display = 'flex'; });

document.getElementById('btn-choice-instant').addEventListener('click', () => { isScheduled = false; setupForm(false); });
document.getElementById('btn-choice-scheduled').addEventListener('click', () => { isScheduled = true; setupForm(true); });

// EVENTO: Cambio de tipo en el modal (Ocultar Título y Fecha)
selectTipo.addEventListener('change', (e) => {
    const val = e.target.value;

    // Reset de estilos de validación
    inputTitulo.classList.remove('is-invalid');
    inputFecha.classList.remove('is-invalid');

    if (val === 'whatsapp') {
        // WhatsApp: Ocultar todo
        containerFecha.classList.add('oculto');
        containerTitulo.classList.add('oculto');
        inputFecha.required = false; inputFecha.value = '';
        inputTitulo.required = false;
        isScheduled = false;
    } else {
        // Correo: Mostrar título siempre
        containerTitulo.classList.remove('oculto');
        inputTitulo.required = true;

        // Fecha depende si era programado
        if (form.dataset.esProgramado === 'true') {
            containerFecha.classList.remove('oculto');
            inputFecha.required = true;
            isScheduled = true;
        } else {
            containerFecha.classList.add('oculto');
            inputFecha.required = false;
        }
    }
});

function setupForm(scheduled, editData = null) {
    closeTipoModal();
    document.getElementById('main-modal').style.display = 'flex';
    document.getElementById('form-error').style.display = 'none';
    form.dataset.esProgramado = scheduled ? 'true' : 'false';

    // Limpiar validaciones visuales previas
    const inputs = form.querySelectorAll('input, textarea, select');
    inputs.forEach(i => i.classList.remove('is-invalid'));

    if (!editData) {
        form.reset();
        acAlumnos.clear(); acCarreras.clear();
        delete form.dataset.editId;
        document.getElementById('main-modal-title').textContent = 'Nuevo Mensaje';
    } else {
        document.getElementById('main-modal-title').textContent = `Editar Mensaje #${editData.id}`;
        form.dataset.editId = editData.id;
        inputTitulo.value = editData.titulo;
        inputDesc.value = editData.descripcion;
        const als = (editData.destino_deudores_info || []).map(d => ({ id: d.id_alumno, name: `${d.apellido}, ${d.nombre}` }));
        const crs = (editData.destino_carrera_info || []).map(c => ({ id: c.id_carrera, name: c.descripcion }));
        acAlumnos.set(als); acCarreras.set(crs);
    }

    if (scheduled) {
        containerFecha.classList.remove('oculto');
        containerTitulo.classList.remove('oculto');
        inputFecha.required = true;
        inputTitulo.required = true;
        selectTipo.innerHTML = `<option value="correo" selected>Correo Electrónico</option>`;
        selectTipo.disabled = true;
        if (editData && editData.fecha_envio) inputFecha.value = toDatetimeLocal(editData.fecha_envio);
    } else {
        // Modo Instantáneo
        containerFecha.classList.add('oculto');
        inputFecha.required = false;
        inputFecha.value = '';

        selectTipo.disabled = false;
        selectTipo.innerHTML = `
      <option value="whatsapp">WhatsApp (Instantáneo)</option>
      <option value="correo">Correo Electrónico</option>
    `;

        if (editData) {
            selectTipo.value = editData.tipo_envio;
            // Disparar evento para ajustar visibilidad según lo que tenga el mensaje editado
            selectTipo.dispatchEvent(new Event('change'));
        } else {
            // Default a WhatsApp al abrir instantáneo nuevo
            selectTipo.value = 'whatsapp';
            selectTipo.dispatchEvent(new Event('change'));
        }
    }
}

// SUBMIT CON VALIDACIÓN VISUAL
form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const btnSave = document.getElementById('btn-save');

    // 1. Validación manual
    let isValid = true;
    const tipoFinal = selectTipo.disabled ? 'correo' : selectTipo.value;

    // Validar Título solo si es Correo
    if (tipoFinal === 'correo' && !inputTitulo.value.trim()) {
        inputTitulo.classList.add('is-invalid');
        isValid = false;
    } else {
        inputTitulo.classList.remove('is-invalid');
    }

    // Validar Descripción siempre
    if (!inputDesc.value.trim()) {
        inputDesc.classList.add('is-invalid');
        isValid = false;
    } else {
        inputDesc.classList.remove('is-invalid');
    }

    if (!isValid) {
        showToast('Por favor completa los campos marcados en rojo', 'error');
        return;
    }

    btnSave.disabled = true;
    btnSave.textContent = 'Guardando...';

    // Si es WhatsApp, el título va vacío visualmente pero el backend puede requerirlo.
    // Ponemos uno por defecto.
    const tituloFinal = (tipoFinal === 'whatsapp') ? 'Mensaje WhatsApp' : inputTitulo.value;

    const payload = {
        titulo: tituloFinal,
        descripcion: inputDesc.value,
        tipo_envio: tipoFinal,
        fecha_envio: inputFecha.value || null,
        en_programado: isScheduled,
        estado_envio: isScheduled ? 'pendiente' : 'enviado',
        destino_deudores: acAlumnos.getIds(),
        destino_carrera: acCarreras.getIds()
    };

    const editId = form.dataset.editId;
    const url = editId ? `${API_BASE}${editId}/` : API_BASE;
    const method = editId ? 'PUT' : 'POST';

    try {
        const res = await fetch(url, {
            method: method,
            headers: { 'Content-Type': 'application/json', 'X-CSRFToken': csrftoken },
            body: JSON.stringify(payload)
        });

        if (!res.ok) throw new Error('Error al guardar');
        const data = await res.json();

        showToast(editId ? 'Actualizado correctamente' : 'Creado con éxito');
        closeMainModal();
        loadData(appState.page);

        // Auto envío WhatsApp
        if (!editId && tipoFinal === 'whatsapp' && !isScheduled) {
            if (data.destino_deudores_info && data.destino_deudores_info.length > 0) {
                setTimeout(() => {
                    if (confirm(`Se guardó el registro. ¿Abrir WhatsApp para enviar a ${data.destino_deudores_info.length} personas?`)) {
                        data.destino_deudores_info.forEach(d => abrirWhatsApp(d.telefono, data.descripcion));
                    }
                }, 500);
            }
        }

    } catch (err) {
        showToast(err.message, 'error');
    } finally {
        btnSave.disabled = false;
        btnSave.textContent = 'Guardar Mensaje';
    }
});

// ==========================================
// CARGA DE DATOS & RENDER
// ==========================================
const tbody = document.getElementById('mensajes-body');
let cacheData = {};

async function loadData(page = 1) {
    tbody.innerHTML = '<tr><td colspan="7" style="text-align:center; padding:20px; color:#999;">Cargando...</td></tr>';
    try {
        const url = new URL(API_BASE, window.location.origin);
        if (appState.filter) url.searchParams.set('tipo_envio', appState.filter);
        if (appState.search) url.searchParams.set('search', appState.search);
        url.searchParams.set('page', page);

        const res = await fetch(url);
        const data = await res.json();
        renderTable(data.results || []);

        appState.page = page;
        document.getElementById('page-info').textContent = `Página ${page}`;
        document.getElementById('btn-prev').disabled = page <= 1;
        document.getElementById('btn-next').disabled = !data.next;
        document.getElementById('mensajes-empty').style.display = (data.results || []).length ? 'none' : 'block';
    } catch (err) { console.error(err); }
}

function renderTable(rows) {
    tbody.innerHTML = '';
    cacheData = {};

    rows.forEach(row => {
        cacheData[row.id] = row;
        const tr = document.createElement('tr');
        tr.dataset.id = row.id;

        let badge = row.tipo_envio === 'whatsapp'
            ? `<span class="badge badge-whatsapp">WhatsApp</span>`
            : `<span class="badge badge-email">Email</span>`;

        let alumnosHtml = '';
        if (row.destino_deudores_info) {
            alumnosHtml = row.destino_deudores_info.map(d => {
                const name = escapeHtml(`${d.apellido}, ${d.nombre}`);
                let btn = '';
                // BOTÓN ENVIAR AHORA (Alineado a la derecha con flex)
                if (row.tipo_envio === 'whatsapp') {
                    const msgSafe = (row.descripcion || '').replace(/'/g, "\\'");
                    btn = `<button class="btn-wa-inline" onclick="event.stopPropagation(); abrirWhatsApp('${d.telefono}', '${msgSafe}')" title="Enviar ahora">
            <svg class="icon" style="width:14px; height:14px;" fill="currentColor" viewBox="0 0 24 24"><path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"/></svg>
          </button>`;
                }
                // Flex container para el nombre y el botón
                return `<div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:4px;">
            <span>${name}</span>
            ${btn}
        </div>`;
            }).join('');
        }

        const carreras = (row.destino_carrera_info || []).map(c => c.descripcion).join(', ');

        tr.innerHTML = `
      <td><span style="color:var(--text-secondary); font-weight:600;">#${row.id}</span></td>
      <td>${escapeHtml(row.titulo)}</td>
      <td><div style="max-width:250px; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;">${escapeHtml(row.descripcion)}</div></td>
      <td>${badge}</td>
      <td>${formatDate(row.fecha_envio)}</td>
      <td style="min-width:200px;">${alumnosHtml}</td>
      <td>${escapeHtml(carreras)}</td>
    `;

        tr.addEventListener('click', (e) => {
            if (e.target.closest('.btn-wa-inline')) return;
            const item = cacheData[row.id];
            if (appState.mode === 'edit') {
                isScheduled = item.en_programado;
                setupForm(isScheduled, item);
            } else if (appState.mode === 'delete') deleteItem(row.id);
        });

        tbody.appendChild(tr);
    });
}

// Listeners
document.getElementById('filtro-tipo').addEventListener('change', e => { appState.filter = e.target.value; loadData(1); });
let st;
document.getElementById('search-input').addEventListener('input', e => { clearTimeout(st); st = setTimeout(() => { appState.search = e.target.value.trim(); loadData(1); }, 400); });
document.getElementById('btn-refresh').addEventListener('click', () => loadData(appState.page));
document.getElementById('btn-prev').addEventListener('click', () => { if (appState.page > 1) loadData(appState.page - 1) });
document.getElementById('btn-next').addEventListener('click', () => loadData(appState.page + 1));

// Delete logic
function deleteItem(id) {
    showConfirm('Eliminar Mensaje', '¿Seguro que deseas eliminar este mensaje?', async () => {
        await fetch(`${API_BASE}${id}/`, { method: 'DELETE', headers: { 'X-CSRFToken': csrftoken } });
        showToast('Eliminado correctamente');
        loadData(appState.page);
        setMode('normal');
    });
}

loadData(1);