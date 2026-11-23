// PROP-12 · Reglas de los campos de la orden de trabajo. «Una regla vive en un solo archivo»:
// este es el único lugar donde se escriben los límites y los mensajes.
//   - Capa navegador: index.html valida con `validar()` antes de enviar y muestra `mensaje`.
//   - Capa base de datos: la migración docs/migraciones/2026-11-23_PROP-12_reglas_y_ordenes_cerradas.sql
//     repite los mismos números en restricciones CHECK y triggers de Postgres.
//     La prueba tests/reglas.test.js falla si los números del SQL no coinciden con este archivo.
// El backend es Supabase: la «capa servidor» son los CHECK y triggers de Postgres (ver docs/ARQUITECTURA.md).
(function () {
  const REGLAS = {
    // Motivo de modificar, anular o marcar como ejecutada una orden (historial_ordenes.motivo)
    motivo: { min: 3, max: 500, nombre: "El motivo" },
    // Detalle libre al anular con «Otro motivo» (forma parte del motivo)
    detalleAnulacion: { min: 3, max: 300, nombre: "El detalle de la anulación" },
    // Justificación que la app redacta al emitir (ordenes_trabajo.justificacion_nota)
    justificacion: { min: 10, max: 2000, nombre: "La justificación" }
  };

  // Devuelve "" si el texto cumple la regla, o el mensaje que verá quien usa la app
  function validar(campo, texto) {
    const r = REGLAS[campo];
    const largo = String(texto || "").trim().length;
    if (largo === 0) return `${r.nombre} es obligatorio.`;
    if (largo < r.min) return `${r.nombre} debe tener al menos ${r.min} caracteres.`;
    if (largo > r.max) return `${r.nombre} admite hasta ${r.max} caracteres; tiene ${largo.toLocaleString("es-CL")}. Acórtelo: no se borró nada de lo escrito.`;
    return "";
  }

  const api = { REGLAS, validar };
  if (typeof module !== "undefined") module.exports = api;   // para la prueba con Node
  if (typeof window !== "undefined") window.REGLAS_CAEX = api;
})();
