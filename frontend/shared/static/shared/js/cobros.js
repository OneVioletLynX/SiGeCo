document.addEventListener("DOMContentLoaded", () => {
  const modal = document.getElementById("altaModal");
  const closeBtn = document.querySelector(".close");
  const btnAgregar = document.querySelector("button"); // tu botón Agregar

  // abrir modal
  btnAgregar.addEventListener("click", () => {
    modal.style.display = "block";
  });

  // cerrar modal
  closeBtn.addEventListener("click", () => (modal.style.display = "none"));
  window.addEventListener("click", (e) => {
    if (e.target === modal) modal.style.display = "none";
  });

  // ==============================
  // 🎨 Selección de meses
  // ==============================
  const meses = document.querySelectorAll(".month");

  meses.forEach((mes) => {
    mes.addEventListener("click", () => {
      const icono = mes.querySelector(".icono-mes");
      const seleccionado = mes.classList.toggle("selected");

      if (seleccionado) {
        // cambia el ícono cuando está seleccionado
        icono.src = icono.src.replace("add.svg", "remove.svg");
      } else {
        // vuelve al ícono original
        icono.src = icono.src.replace("remove.svg", "add.svg");
      }
    });
  });
});

document.addEventListener("DOMContentLoaded", () => {
  const metodoPagoSelect = document.getElementById("metodo_pago");
  const campoComprobante = document.getElementById("campo-comprobante");
  const campoTarjeta = document.getElementById("campo-tarjeta");

  metodoPagoSelect.addEventListener("change", () => {
    const metodo = metodoPagoSelect.value;

    // ocultar todos primero
    campoComprobante.classList.add("hidden");
    campoTarjeta.classList.add("hidden");

    // mostrar según la opción
    if (metodo === "transferencia") {
      campoComprobante.classList.remove("hidden");
    } else if (metodo === "tarjeta") {
      campoTarjeta.classList.remove("hidden");
    }
  });
});
