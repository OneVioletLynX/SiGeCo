// Desplegar submenú al hacer clic
document.querySelectorAll('.submenu-toggle').forEach(toggle => {
    toggle.addEventListener('click', e => {
        e.preventDefault();
        const parent = toggle.parentElement;
        parent.classList.toggle('open');
    });
});

const table = document.getElementById("sortableTable");
const headers = table.querySelectorAll("th");

headers.forEach((header, index) => {
    header.addEventListener("click", () => {
    const isAscending = header.classList.contains("asc");
    const direction = isAscending ? -1 : 1;

    // limpiar clases activas
    headers.forEach(h => h.classList.remove("active", "asc"));

    // activar el actual
    header.classList.add("active");
    if (!isAscending) header.classList.add("asc");

    // ordenar filas
    const rows = Array.from(table.tBodies[0].rows);
    rows.sort((a, b) => {
        const aText = a.cells[index].textContent.trim();
        const bText = b.cells[index].textContent.trim();
        const aNum = parseFloat(aText);
        const bNum = parseFloat(bText);
        if (!isNaN(aNum) && !isNaN(bNum)) {
        return (aNum - bNum) * direction;
        }
        return aText.localeCompare(bText) * direction;
    });

    rows.forEach(row => table.tBodies[0].appendChild(row));
    });
});