document.addEventListener("DOMContentLoaded", () => {
    const links = document.querySelectorAll(".sidebar nav a");
    const current = window.location.pathname;

    links.forEach(link => {
        if (link.getAttribute("href") === current) {
            link.classList.add("selected");
        }
    });
});
