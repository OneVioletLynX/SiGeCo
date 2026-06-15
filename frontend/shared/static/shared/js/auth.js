// Funciones de autenticación globales — cargadas desde base.html antes que los scripts de página

window.getToken = function () {
  return localStorage.getItem("sigeco_access") || "";
};

window.logout = function () {
  localStorage.removeItem("sigeco_access");
  localStorage.removeItem("sigeco_refresh");
  localStorage.removeItem("sigeco_rol");
  localStorage.removeItem("sigeco_nombre");
  localStorage.removeItem("sigeco_permisos");
  document.cookie = "sigeco_access=; path=/; max-age=0";
  window.location.href = "http://127.0.0.1:8001/";
};

// Semáforo: evita múltiples refreshes simultáneos
window._refreshPromise = null;

window.tryRefreshToken = async function () {
  if (window._refreshPromise) return window._refreshPromise;

  window._refreshPromise = (async () => {
    try {
      const refresh = localStorage.getItem("sigeco_refresh");
      if (!refresh) return false;

      const resp = await fetch("http://127.0.0.1:8000/api/token/refresh/", {
        method:  "POST",
        headers: { "Content-Type": "application/json" },
        body:    JSON.stringify({ refresh }),
      });

      if (!resp.ok) return false;
      const data = await resp.json();
      if (!data.access) return false;

      localStorage.setItem("sigeco_access", data.access);
      document.cookie = `sigeco_access=${data.access}; path=/`;
      if (data.refresh) localStorage.setItem("sigeco_refresh", data.refresh);
      return true;
    } catch {
      return false;
    } finally {
      window._refreshPromise = null;
    }
  })();

  return window._refreshPromise;
};

window.authFetch = async function (url, options = {}) {
  const token = window.getToken();
  if (!token) { window.logout(); return; }

  const makeHeaders = () => ({
    ...(options.headers || {}),
    "Authorization": `Bearer ${window.getToken()}`,
  });

  let resp = await fetch(url, { ...options, headers: makeHeaders() });

  if (resp.status === 401) {
    const refreshed = await window.tryRefreshToken();
    if (!refreshed) { window.logout(); return; }
    resp = await fetch(url, { ...options, headers: makeHeaders() });
    if (resp.status === 401) { window.logout(); return; }
  }

  return resp;
};
