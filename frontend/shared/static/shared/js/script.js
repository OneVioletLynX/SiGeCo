document.addEventListener("DOMContentLoaded", () => {
    const links = document.querySelectorAll("#sidebar nav a");
    const current = window.location.pathname;

    links.forEach(link => {
        const href = link.getAttribute("href");
        if (href && href !== "#" && current.startsWith(href)) {
            link.classList.add("selected");
        }
    });
});


window.showAlert = function(message, type = "default") {
    const alertBox = document.getElementById("customAlert");
    const alertMsg = document.getElementById("customAlertMessage");

    alertMsg.textContent = message;

    // Remover clases antiguas
    alertBox.className = "custom-alert";

    if (type !== "default") {
        alertBox.classList.add(type);
    }

    // Mostrar alerta correctamente
    alertBox.classList.add("show");

    // Ocultar después
    setTimeout(() => {
        alertBox.classList.remove("show");
    }, 2500);
};

window.showConfirm = function(message, title = "Confirmación") {
    return new Promise(resolve => {
        const modal = document.getElementById("confirmModal");
        const msg = document.getElementById("confirmMessage");
        const ttl = document.getElementById("confirmTitle");
        const cancel = document.getElementById("confirmCancel");
        const accept = document.getElementById("confirmAccept");

        msg.textContent = message;
        ttl.textContent = title;

        // 👇 MOSTRAR CORRECTAMENTE
        modal.classList.remove("hidden");
        modal.style.display = "flex";  

        const close = () => {
            modal.style.display = "none";
            modal.classList.add("hidden");
        };

        cancel.onclick = () => { close(); resolve(false); };
        accept.onclick = () => { close(); resolve(true); };
    });
};
