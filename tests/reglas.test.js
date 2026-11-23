// PROP-12 · «Una regla vive en un solo archivo»: src/reglas.js es la fuente.
// Esta prueba falla si la migración SQL usa números distintos, o si validar() no responde como se espera.
// Ejecutar: node tests/reglas.test.js
const fs = require("fs");
const path = require("path");
const { REGLAS, validar } = require("../src/reglas.js");

const sql = fs.readFileSync(path.join(__dirname, "../docs/migraciones/2026-11-23_PROP-12_reglas_y_ordenes_cerradas.sql"), "utf8");
let fallas = 0;
const ok = (cond, msg) => { console.log((cond ? "OK   " : "FALLA") + " " + msg); if (!cond) fallas++; };

// 1. El SQL repite los límites de reglas.js
const limite = nombre => {
  const m = sql.match(new RegExp(`CONSTRAINT ${nombre}\\s+CHECK \\(char_length\\(btrim\\(\\w+\\)\\) BETWEEN (\\d+) AND (\\d+)\\)`));
  return m ? [Number(m[1]), Number(m[2])] : null;
};
const motivo = limite("chk_historial_motivo_largo");
const justif = limite("chk_orden_justificacion_largo");
ok(motivo && motivo[0] === REGLAS.motivo.min && motivo[1] === REGLAS.motivo.max,
  `motivo: SQL ${motivo} = reglas.js ${REGLAS.motivo.min}-${REGLAS.motivo.max}`);
ok(justif && justif[0] === REGLAS.justificacion.min && justif[1] === REGLAS.justificacion.max,
  `justificación: SQL ${justif} = reglas.js ${REGLAS.justificacion.min}-${REGLAS.justificacion.max}`);
ok(REGLAS.detalleAnulacion.max + "Otro motivo: ".length <= REGLAS.motivo.max,
  "el detalle de anulación cabe en el motivo que guarda la base");

// 2. validar() con los intentos de rotura del profesor
ok(validar("motivo", "") === "El motivo es obligatorio.", "campo vacío → obligatorio");
ok(validar("motivo", "     ") === "El motivo es obligatorio.", "solo espacios → obligatorio");
ok(/al menos 3/.test(validar("motivo", "ok")), "2 letras → mínimo 3");
ok(validar("motivo", "taller sin horas hombre") === "", "motivo normal → válido");
const largo = validar("motivo", "x".repeat(5000));
ok(/hasta 500/.test(largo) && /5\.000/.test(largo) && /no se borró/.test(largo), "5.000 letras → rechazado con mensaje propio: " + largo);
ok(validar("motivo", "x".repeat(500)) === "", "500 letras exactas → válido");

process.exitCode = fallas ? 1 : 0;
console.log(fallas ? `${fallas} falla(s)` : "Todas las pruebas de reglas pasan");
