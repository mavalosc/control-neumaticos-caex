// PROP-12 · Prueba de pantalla con una base SIMULADA (no toca Supabase): guardado sin optimismo, estados y
// los 5 intentos de rotura. Requiere jsdom: npm install jsdom@24 --no-save && node tests/pantalla-prop12.test.js
const { JSDOM, VirtualConsole } = require("jsdom");
const fs = require("fs");
const raiz = require("path").join(__dirname, "../src/") + "/";
let html = fs.readFileSync(raiz + "index.html", "utf8").replace(/<script[^>]+src=[^>]+><\/script>/g, "");
const reglasSrc = fs.readFileSync(raiz + "reglas.js", "utf8");
const vc = new VirtualConsole(); vc.on("jsdomError", e => { if (!/scrollTo/.test(e.message)) console.log("JSDOM", e.message); });

let fallas = 0;
const ok = (c, m) => { console.log((c ? "OK   " : "FALLA") + " " + m); if (!c) fallas++; };
const espera = ms => new Promise(r => setTimeout(r, ms));

// --- Base simulada ---
let modo = "ok";          // ok | red | cerrada | lenta
let offline = false;
let pendiente = null;      // para cargar lenta
const llamadas = [];
let base = null;           // { orders, windows } se inicia con los datos de ejemplo
const clon = x => JSON.parse(JSON.stringify(x));
function fallar() {
  if (modo === "red") throw new Error("TypeError: Failed to fetch");
  if (modo === "cerrada") throw Object.assign(new Error("La orden ot-0068 está anulada y no admite cambios."), { code: "P0001", hint: "orden_cerrada" });
}
const DB = {
  activo: true, fijarUsuario() {},
  async cargar() {
    llamadas.push("cargar");
    if (modo === "lenta") await new Promise(r => { pendiente = r; });
    await espera(5); fallar();
    return { trucks: w.eval("INITIAL_TRUCKS"), knownTires: w.eval("INITIAL_KNOWN_TIRES"), damages: w.eval("INITIAL_DAMAGES"), deteccion: {},
      orders: clon(base.orders), windows: clon(base.windows) };
  },
  async leerPredicciones() { return { predicciones: {}, modeloVersion: null }; },
  async emitirOrden(o) { llamadas.push("emitir:" + o.codigo); await espera(20); fallar();
    const win = base.windows.find(x => x.id === o.ventanaId); win.libres--;
    base.orders.unshift([o.codigo, "hoy", o.serial, o.tipo, o.nota, win.dia, win.turno, o.horas, "", o.origen, "programada", ["orden emitida"]]); },
  async modificarOrden(c, x) { llamadas.push("modificar:" + c + ":" + x.motivo.length); await espera(10); fallar(); },
  async anularOrden(c, m) { llamadas.push("anular:" + c + ":" + m); await espera(10); fallar();
    const o = base.orders.find(z => z[0] === c); o[10] = "anulada"; o[11].push("hoy · pr***@prueba.cl · orden anulada · motivo: " + m); },
  async ejecutarOrden(c, m) { llamadas.push("ejecutar:" + c + ":" + m); await espera(10); fallar();
    const o = base.orders.find(z => z[0] === c); o[10] = "ejecutada"; o[11].push("hoy · pr***@prueba.cl · orden ejecutada · motivo: " + m); },
  async registrarDano() { llamadas.push("dano"); await espera(10); fallar(); }
};

const dom = new JSDOM(html, { runScripts: "dangerously", url: "http://localhost/src/index.html", pretendToBeVisual: true, virtualConsole: vc,
  beforeParse(win) {
    win.DB = DB; win.eval(reglasSrc);
    Object.defineProperty(win.navigator, "onLine", { get: () => !offline });
    win.localStorage.setItem("caex_usuario_email", "prueba@prueba.cl");
  } });
const w = dom.window;
const $ = () => w.document.getElementById("app");
const toast = () => w.document.getElementById("toast").textContent.trim();
const ir = h => { w.location.hash = h; w.eval("route()"); };

(async () => {
  // usuario: si la clave del almacenamiento es otra, ingresar
  modo = "lenta";
  base = { orders: clon(w.eval("INITIAL_ORDERS")), windows: clon(w.eval("INITIAL_WINDOWS")) };
  await espera(30);
  if (!w.eval("usuarioEmail")) { w.eval("ingresar('prueba@prueba.cl')"); }
  // A. Estado de carga
  ok(/Cargando datos/.test($().textContent), "A1 al abrir muestra «Cargando datos…» (antes: pantalla en blanco)");
  modo = "red"; pendiente(); await espera(40);
  ok(/No se pudo conectar con la base de datos/.test($().textContent) && /Reintentar/.test($().innerHTML), "A2 base caída al abrir: error con «Reintentar» (antes: modo local con éxitos falsos)");
  ok(w.eval("DB.activo") === true, "A3 no se cambia en silencio a modo local");
  ir("#/o");
  ok(/No se pudo conectar/.test($().textContent), "A4 ninguna pantalla muestra datos mientras la base no carga");
  modo = "ok"; await w.eval("iniciarDatos()");
  ok(w.eval("cargaInicial") === "lista" && /Órdenes de Trabajo/.test($().textContent), "A5 Reintentar con la base disponible carga los datos");

  // B. Contadores y estado vacío
  const kpis = [...$().querySelectorAll(".text-3xl")].map(x => x.textContent.trim());
  ok(kpis.join(",") === "5,1,1", "B1 contadores reales Programadas/Ejecutadas/Anuladas = " + kpis.join(","));
  w.eval("searchOrderQuery='zzzz'; renderOrders()");
  ok(/Ninguna orden coincide/.test($().textContent) && /Ver todas las órdenes/.test($().textContent), "B2 estado vacío con explicación y salida");
  w.eval("searchOrderQuery=''; renderOrders()");
  ok([...$().querySelectorAll("button")].some(b => b.textContent.trim() === "Ver"), "B3 órdenes cerradas tienen botón «Ver»");

  // C. Registro inexistente (T5) y orden cerrada
  ir("#/e/ot-9999");
  ok(/La orden ot-9999 no existe/.test($().textContent) && /Ir a Órdenes/.test($().textContent), "C1 T5 ot-9999: aviso «no existe» (antes: volvía sin mensaje)");
  ir("#/a/NO-EXISTE");
  ok(/no existe/.test($().textContent) && /No se creó ninguna orden/.test($().textContent), "C2 agendar un neumático inexistente: aviso");
  ir("#/n/NO-EXISTE");
  ok(/El neumático NO-EXISTE no existe/.test($().textContent), "C3 ficha inexistente: aviso");
  ir("#/e/ot-0052");
  ok(/Solo lectura/.test($().textContent) && !$().querySelector("textarea") && !/Guardar Modificaciones/.test($().textContent), "C4 orden cerrada por su dirección: solo lectura, sin formularios");
  ok(/Motivo del cierre/.test($().textContent), "C5 muestra el motivo del cierre y el historial");

  // D. Emitir: sin conexión (T4), doble clic (T2) y éxito confirmado
  const serial = w.eval("state.orders.length") && w.eval("getTires().find(t => t.h > 300).serial");
  const nAntes = w.eval("state.orders.length");
  ir("#/a/" + serial);
  ok(!/ERP|SAP/.test($().textContent), "D1 Agendar no menciona un ERP");
  const win = w.eval("state.windows.find(x => x.libres > 0)");
  w.eval(`selectedWindowId=${win.id}; riesgoAceptado=true; renderSchedule('${serial}')`);
  offline = true;
  await w.eval(`emitirOrden('${serial}')`);
  ok(w.eval("state.orders.length") === nAntes && !llamadas.some(x => x.startsWith("emitir")), "D2 T4 sin conexión: no hay orden fantasma ni intento de escritura");
  ok(/Sin conexión/.test(toast()) && /Nada se guardó/.test(toast()), "D3 T4 mensaje propio: " + toast());
  ok(w.location.hash === "#/a/" + serial, "D4 T4 se queda en Agendar con la ventana elegida");
  offline = false; modo = "red";
  await w.eval(`emitirOrden('${serial}')`);
  ok(w.eval("state.orders.length") === nAntes && /Sin conexión/.test(toast()), "D5 la red cae durante el envío: nada aparece guardado");
  ok(!w.document.getElementById("btn-emitir").disabled, "D6 el botón vuelve a estar disponible para reintentar");
  modo = "ok";
  const p1 = w.eval(`emitirOrden('${serial}')`);
  const b = w.document.getElementById("btn-emitir");
  ok(b.disabled && /Guardando/.test(b.textContent), "D7 mientras guarda: botón «Guardando la orden…» deshabilitado");
  const p2 = w.eval(`emitirOrden('${serial}')`);
  await Promise.all([p1, p2]); await espera(20);
  ok(llamadas.filter(x => x.startsWith("emitir")).length === 2, "D8 T2 doble clic: una sola escritura (" + llamadas.filter(x => x.startsWith("emitir")).length + " en total con el intento fallido)");
  ok(w.eval("state.orders.length") === nAntes + 1 && /guardada en la base/.test(toast()), "D9 éxito solo tras la confirmación: " + toast());

  // E. Modificar: texto larguísimo (T3), campo vacío (T1), otra pestaña cerró la orden
  const id = w.eval("state.orders.find(o => o[10]==='programada')[0]");
  ir("#/e/" + id);
  const ta = w.document.getElementById("motivo-cambio");
  ta.value = "x".repeat(5000); ta.dispatchEvent(new w.Event("input"));
  ok(w.document.getElementById("btn-guardar-ot").disabled, "E1 T3 5.000 letras: Guardar deshabilitado (antes: habilitado y no guardaba)");
  ok(/hasta 500/.test(w.document.getElementById("motivo-cambio-error").textContent), "E2 T3 mensaje: " + w.document.getElementById("motivo-cambio-error").textContent);
  ok(w.document.getElementById("motivo-cambio").value.length === 5000, "E3 T3 lo escrito no se borra");
  ok(/5\.000\/500/.test(w.document.getElementById("motivo-cambio-contador").textContent), "E4 contador de caracteres");
  ta.value = "   "; ta.dispatchEvent(new w.Event("input"));
  ok(w.document.getElementById("btn-guardar-ot").disabled && /obligatorio/.test(w.document.getElementById("motivo-cambio-error").textContent), "E5 T1 solo espacios: obligatorio");
  ta.value = "taller sin horas hombre"; ta.dispatchEvent(new w.Event("input"));
  modo = "cerrada";
  await w.eval(`guardarCambiosOrden('${id}')`);
  ok(/no admite cambios/.test(toast()) && /otra pestaña/.test(toast()), "E6 dos pestañas: " + toast());
  ok(w.document.getElementById("motivo-cambio").value === "taller sin horas hombre" && w.location.hash === "#/e/" + id, "E7 tras el error, el motivo sigue escrito y no cambia de pantalla");
  modo = "ok";

  // F. Anular con «Otro motivo» (órdenes de prueba) y marcar como ejecutada
  w.eval("editState.motivoAnulacion='Otro motivo'; renderEditOrder('" + id + "')");
  ok(w.document.getElementById("detalle-anulacion"), "F1 «Otro motivo» pide describirlo");
  const d = w.document.getElementById("detalle-anulacion"); d.value = "PRUEBA DE ROTURA"; d.dispatchEvent(new w.Event("input"));
  w.eval("editState.confirmingAnulacion=true; renderEditOrder('" + id + "')");
  await w.eval(`confirmarAnulacion('${id}')`);
  ok(llamadas.includes(`anular:${id}:Otro motivo: PRUEBA DE ROTURA`), "F2 anulación en una sola llamada con el motivo completo");
  ir("#/e/" + id);
  ok(/anulada/.test($().textContent) && /PRUEBA DE ROTURA/.test($().textContent) && /Solo lectura/.test($().textContent), "F3 la orden anulada queda en solo lectura con su motivo");
  const id2 = w.eval("state.orders.find(o => o[10]==='programada')[0]");
  ir("#/e/" + id2);
  const te = w.document.getElementById("motivo-ejecucion"); te.value = "retiro hecho en turno A"; te.dispatchEvent(new w.Event("input"));
  ok(!w.document.getElementById("btn-ejecutar-ot").disabled, "F4 «Marcar como ejecutada» se habilita con la observación");
  await w.eval(`marcarEjecutada('${id2}')`);
  ir("#/o");
  const k2 = [...$().querySelectorAll(".text-3xl")].map(x => x.textContent.trim());
  ok(k2[1] === "2" && k2[2] === "2", "F5 contadores tras ejecutar y anular: " + k2.join(","));

  // G. Corrección de daño: el aviso llega después de la base
  modo = "red";
  const tz = w.eval("getTires().find(t => t.nivel > 0)");
  ir("#/n/" + tz.serial);
  await w.eval(`corregirClasificacion('${tz.serial}', ${tz.nivel === 1 ? 2 : 1})`);
  ok(!/Corrección guardada/.test(toast()) && /Sin conexión/.test(toast()), "G1 corrección sin red: no dice «guardada»");

  console.log(fallas ? `\n${fallas} falla(s)` : "\nTodas las pruebas de PROP-12 pasan");
  process.exit(fallas ? 1 : 0);
})().catch(e => { console.error("ERROR", e); process.exit(2); });
