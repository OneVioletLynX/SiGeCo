/**
 * Abre una pestaña de WhatsApp con el número y mensaje listos.
 * @param {string} telefonoOriginal - El número tal cual viene de la base de datos.
 * @param {string} mensaje - El texto que se quiere enviar.
 */
function enviarWhatsApp(telefonoOriginal, mensaje) {
    if (!telefonoOriginal) {
        alert("El usuario no tiene número de teléfono registrado.");
        return;
    }

    // 1. Limpiar el número: Elimina todo lo que NO sea un número.
    let telefonoLimpio = telefonoOriginal.toString().replace(/\D/g, '');

    // 2. Lógica para Argentina (54 + 9 + código área + número)
    // Si el número no empieza con 54, asumimos que es local.
    if (!telefonoLimpio.startsWith('54')) {
        // Agregamos 549 para móviles de Argentina
        telefonoLimpio = '549' + telefonoLimpio;
    }

    // 3. Codificar el mensaje para URL
    const mensajeCodificado = encodeURIComponent(mensaje);

    // 4. Generar la URL oficial
    const url = `https://wa.me/${telefonoLimpio}?text=${mensajeCodificado}`;

    // 5. Abrir en nueva pestaña
    window.open(url, '_blank');
}