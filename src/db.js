// Capa de datos del prototipo: lee y escribe en Supabase y entrega a las pantallas
// el mismo objeto `state` que usa el modo local (localStorage).
// Requiere: config.js (window.CAEX_CONFIG) y supabase-js v2 cargado desde CDN.
(function () {
  const cfg = window.CAEX_CONFIG || {};
  const cliente = cfg.SUPABASE_URL && cfg.SUPABASE_ANON_KEY && window.supabase
    ? window.supabase.createClient(cfg.SUPABASE_URL, cfg.SUPABASE_ANON_KEY, {
        // PROP-12: si la base no responde en 15 s, se avisa en vez de esperar sin fin
        global: { fetch: (url, op = {}) => fetch(url, { ...op, signal: op.signal || AbortSignal.timeout(15000) }) }
      })
    : null;

  // Índices auxiliares que se rellenan en cada carga
  const idNeumatico = {};   // serial -> uuid
  const ultimaMedicion = {}; // serial -> codigo_medicion
  const idOrden = {};       // 'ot-0068' -> uuid

  const TZ = "America/Santiago";
  const dos = n => String(n).padStart(2, "0");
  function partes(ts) {
    const p = {};
    new Intl.DateTimeFormat("es-CL", { timeZone: TZ, year: "numeric", month: "2-digit", day: "2-digit", hour: "2-digit", minute: "2-digit", hour12: false })
      .formatToParts(new Date(ts)).forEach(x => { p[x.type] = x.value; });
    return p;
  }
  const fechaCL = ts => { const p = partes(ts); return `${p.day}-${p.month}-${p.year}`; };
  const fechaHoraCL = ts => { const p = partes(ts); return `${p.day}-${p.month}-${p.year} ${p.hour === "24" ? "00" : p.hour}:${p.minute}`; };
  const diaCL = iso => iso.split("-").reverse().join("-"); // '2026-09-29' -> '29-09-2026'
  const zonaDe = h => h == null ? "gris" : h < 200 ? "rojo" : h < 500 ? "amarillo" : "verde";
  const ACCION = { modificacion: "modificación de orden", anulacion: "orden anulada", ejecucion: "orden ejecutada" };

  // PROP-08: email de quien opera; queda en historial_ordenes.autor. La app solo lo lee abreviado
  // (vista_historial_ordenes); la columna completa no es legible con la clave pública.
  let autorActual = "planificador";
  const fijarUsuario = email => { autorActual = email || "planificador"; };

  // PROP-12: el error conserva el código de Postgres para que la app lo traduzca a un mensaje propio
  function revisar({ data, error }) {
    if (error) throw Object.assign(new Error(error.message), { code: error.code, hint: error.hint, details: error.details });
    return data;
  }

  async function cargar() {
    const [vista, ventanas, ordenes] = await Promise.all([
      cliente.from("vista_tablero_turno").select("*").order("caex_codigo").order("posicion").limit(5000).then(revisar),
      cliente.from("ventanas_taller").select("*").eq("reservable", true).order("dia").order("id").then(revisar),
      cliente.from("ordenes_trabajo")
        .select("id,codigo,fecha_emision,tipo_intervencion,justificacion_nota,horas_remanentes_emision,medicion_codigo,origen_detalle,estado,neumaticos(serial),ventanas_taller(id,dia,turno)")
        .order("fecha_emision", { ascending: false }).then(revisar)
    ]);
    const historialPorOrden = {};
    (await leerHistorial()).forEach(h => (historialPorOrden[h.orden_id] ||= []).push(h));
    if (!vista.length) throw new Error("La base no tiene neumáticos. Ejecuta docs/seed.sql en Supabase.");

    const trucks = [], knownTires = {}, damages = {}, deteccion = {};
    const porCamion = new Map();
    vista.forEach(r => {
      if (!porCamion.has(r.caex_codigo)) {
        const camion = [r.caex_codigo, r.caex_modelo, Number(r.horometro_h).toLocaleString("es-CL") + " h", [null, null, null, null, null, null]];
        porCamion.set(r.caex_codigo, camion);
        trucks.push(camion);
      }
      const key = r.caex_codigo.split("-")[1] + "-" + r.posicion;
      porCamion.get(r.caex_codigo)[3][r.posicion - 1] = r.horas_remanentes_calculadas;
      // PROP-11: [5] horas de uso desde el montaje (dato sintético; null si la migración aún no se ejecuta)
      knownTires[key] = [r.neumatico_serial, Number(r.profundidad_mm), Number(r.tasa_desgaste_por_100h),
        r.fecha_pasada ? fechaCL(r.fecha_pasada) : "sin pasada", Number(r.temperatura_flanco_c),
        r.horas_uso_h == null ? null : Number(r.horas_uso_h)];
      const nivel = Number(r.nivel_dano);
      if (nivel > 0) damages[key] = [nivel, r.detalle_dano, r.confianza_ia == null ? 1 : Number(r.confianza_ia), !!r.validado_por_humano];
      // PROP-11: última detección de la visión artificial, que una corrección humana no reemplaza
      if (r.detalle_detectado != null && Number(r.nivel_detectado) > 0)
        deteccion[key] = [Number(r.nivel_detectado), r.detalle_detectado, r.confianza_detectada == null ? null : Number(r.confianza_detectada)];
      idNeumatico[r.neumatico_serial] = r.neumatico_id;
      ultimaMedicion[r.neumatico_serial] = r.codigo_medicion;
    });

    const orders = ordenes.map(o => {
      idOrden[o.codigo] = o.id;
      const hist = (historialPorOrden[o.id] || [])
        .sort((a, b) => new Date(a.fecha_evento) - new Date(b.fecha_evento))
        .map(h => h.accion === "creacion"
          ? `${fechaHoraCL(h.fecha_evento)} · ${h.autor} · ${h.motivo}`
          : `${fechaHoraCL(h.fecha_evento)} · ${h.autor} · ${ACCION[h.accion] || h.accion} · motivo: ${h.motivo}`);
      return [o.codigo, fechaHoraCL(o.fecha_emision), o.neumaticos ? o.neumaticos.serial : "", o.tipo_intervencion,
        o.justificacion_nota, o.ventanas_taller ? diaCL(o.ventanas_taller.dia) : "", o.ventanas_taller ? o.ventanas_taller.turno : "",
        o.horas_remanentes_emision, o.medicion_codigo || "", o.origen_detalle || "", o.estado, hist];
    });

    const windows = ventanas.map(w => ({
      id: w.id, dia: diaCL(w.dia), turno: w.turno, libres: w.cupos_libres, en: w.horas_hasta_ventana, max: w.cupos_totales
    }));

    return { trucks, knownTires, damages, deteccion, orders, windows };
  }

  // Historial con el autor abreviado; si la vista aún no existe en la base, usa la tabla (antes de PROP-08)
  async function leerHistorial() {
    const vista = await cliente.from("vista_historial_ordenes").select("orden_id,fecha_evento,autor,accion,motivo").limit(10000);
    if (!vista.error) return vista.data;
    return revisar(await cliente.from("historial_ordenes").select("orden_id,fecha_evento,autor,accion,motivo").limit(10000));
  }

  // PROP-12: cada cambio de una orden es UNA escritura en el historial; el trigger aplicar_evento_orden
  // aplica el cambio a la orden en la misma transacción (docs/migraciones/2026-11-23_PROP-12_...).
  async function historial(codigo, accion, motivo, detalles = null) {
    if (!idOrden[codigo]) throw Object.assign(new Error(`La orden ${codigo} no existe.`), { code: "no_existe" });
    revisar(await cliente.from("historial_ordenes").insert({ orden_id: idOrden[codigo], autor: autorActual, accion, motivo, detalles }));
  }

  async function emitirOrden({ codigo, serial, ventanaId, tipo, nota, horas, origen }) {
    const fila = revisar(await cliente.from("ordenes_trabajo").insert({
      codigo, neumatico_id: idNeumatico[serial], ventana_id: ventanaId, tipo_intervencion: tipo,
      justificacion_nota: nota, horas_remanentes_emision: horas, medicion_codigo: ultimaMedicion[serial] || null,
      origen_detalle: origen, estado: "programada"
    }).select("id").single());
    idOrden[codigo] = fila.id;
    // La orden ya quedó guardada: si falla solo la línea de creación del historial, no se informa
    // «nada se guardó» (sería falso); se registra en la consola y la orden sigue válida.
    try { await historial(codigo, "creacion", "orden emitida"); }
    catch (e) { console.warn(`Orden ${codigo} guardada sin la línea de creación del historial`, e); }
  }

  async function modificarOrden(codigo, { ventanaId, motivo }) {
    await historial(codigo, "modificacion", motivo, ventanaId ? { ventana_id: ventanaId } : null);
  }

  async function anularOrden(codigo, motivo) {
    await historial(codigo, "anulacion", motivo);
  }

  async function ejecutarOrden(codigo, motivo) {
    await historial(codigo, "ejecucion", motivo);
  }

  // PROP-11: la corrección conserva la descripción y la confianza de la detección; el autor es el email (PROP-08)
  async function registrarDano(serial, nivel, descripcion, confianza) {
    revisar(await cliente.from("danos_neumaticos").insert({
      neumatico_id: idNeumatico[serial], severidad: String(nivel), descripcion: nivel > 0 ? descripcion : "Sin daño",
      confianza_ia: confianza == null ? 1 : confianza, validado_por_humano: true, usuario_validador: autorActual
    }));
  }

  // lecturas: [{ serial, h, mm, rate, temp, horometro }]
  async function registrarPasada(lecturas) {
    const sello = Date.now().toString(36);
    revisar(await cliente.from("mediciones").insert(lecturas.map((t, i) => ({
      codigo_medicion: `med-${sello}-${i + 1}`, neumatico_id: idNeumatico[t.serial], horas_operacion: t.horometro,
      profundidad_mm: t.mm, tasa_desgaste_por_100h: t.rate, tipo_tasa: t.h < 500 ? "observada" : "nominal",
      temperatura_flanco_c: t.temp, horas_remanentes_calculadas: t.h, zona_calculada: zonaDe(t.h)
    }))));
  }

  // Explorador de datos: lee una tabla completa (por bloques de 1.000 filas) con datos legibles de sus relaciones.
  const RELACIONES = {
    neumaticos: "*, camiones(codigo)",
    mediciones: "*, neumaticos(serial, posicion, camiones(codigo))",
    danos_neumaticos: "*, neumaticos(serial), mediciones(codigo_medicion)",
    ordenes_trabajo: "*, neumaticos(serial), ventanas_taller(dia, turno)",
    historial_ordenes: "*, ordenes_trabajo(codigo)"
  };
  // PROP-08 y PROP-11: el email de quien opera solo se lee abreviado
  const FUENTE = { historial_ordenes: "vista_historial_ordenes", danos_neumaticos: "vista_danos_neumaticos" };

  // { neumaticos: { serial: "x", camiones: { codigo: "y" } } } -> { "neumaticos.serial": "x", "neumaticos.camiones.codigo": "y" }
  function aplanar(fila, prefijo = "", out = {}) {
    for (const [k, v] of Object.entries(fila)) {
      const clave = prefijo + k;
      if (v && typeof v === "object" && !Array.isArray(v)) aplanar(v, clave + ".", out);
      else if (Array.isArray(v)) out[clave] = v.map(textoElemento).join(" · ");   // ej. las 3 causas SHAP
      else out[clave] = v;
    }
    return out;
  }

  // { etiqueta: "Presión de inflado", efecto: "aumenta", peso_pct: 23.8 } -> "Presión de inflado (aumenta 23.8 %)"
  const textoElemento = x => x && typeof x === "object"
    ? (x.etiqueta ? `${x.etiqueta} (${x.efecto} ${x.peso_pct} %)` : JSON.stringify(x)) : String(x);

  // El primer bloque trae el total de filas; los demás bloques se piden en paralelo (30.000 filas en segundos).
  async function leerTabla(nombre) {
    let fuente = FUENTE[nombre] || nombre;
    let columnas = fuente === nombre ? RELACIONES[nombre] || "*" : "*";
    let primero = await cliente.from(fuente).select(columnas, { count: "exact" }).range(0, 999);
    if (primero.error && fuente !== nombre) {   // la vista aún no existe en la base: lee la tabla
      fuente = nombre; columnas = RELACIONES[nombre] || "*";
      primero = await cliente.from(fuente).select(columnas, { count: "exact" }).range(0, 999);
    }
    const filas = revisar(primero);
    const total = primero.count ?? filas.length;
    const bloques = [];
    for (let desde = 1000; desde < total; desde += 1000)
      bloques.push(cliente.from(fuente).select(columnas).range(desde, desde + 999).then(revisar));
    for (const bloque of await Promise.all(bloques)) filas.push(...bloque);
    return filas.map(f => aplanar(f));
  }

  // PROP-06: predicción del modelo entrenado con datos de terreno simulados (si las tablas aún no existen, devuelve vacío)
  async function leerPredicciones() {
    const [pred, ver] = await Promise.all([
      cliente.from("vista_prediccion_actual").select("serial,modelo_version,fecha_prediccion,profundidad_mm,tasa_prevista_mm_100h,horas_remanentes_modelo,causas,origen").limit(5000),
      cliente.from("modelo_versiones").select("*").order("fecha_entrenamiento", { ascending: false }).limit(1)
    ]);
    if (pred.error || ver.error) return { predicciones: {}, modeloVersion: null };
    return {
      predicciones: Object.fromEntries(pred.data.map(p => [p.serial, p])),
      modeloVersion: ver.data[0] || null
    };
  }

  // PROP-07: datos reales anonimizados (resumen para la página Modelos; si las tablas aún no existen, devuelve null)
  async function leerDatosReales() {
    const contar = t => cliente.from(t).select("*", { count: "exact", head: true });
    const [alertas, velocidad, ver] = await Promise.all([
      contar("alertas_tpms"), contar("eventos_velocidad"),
      cliente.from("riesgo_versiones").select("*").order("fecha_entrenamiento", { ascending: false }).limit(1)
    ]);
    if (alertas.error || velocidad.error || ver.error) return null;
    const version = ver.data[0] || null;
    const riesgo = version ? revisar(await cliente.from("riesgo_posiciones").select("*")
      .eq("modelo_version", version.version).order("probabilidad", { ascending: false })) : [];
    return { alertas: alertas.count, velocidad: velocidad.count, version, riesgo };
  }

  window.DB = { activo: !!cliente, fijarUsuario, cargar, emitirOrden, modificarOrden, anularOrden, ejecutarOrden, registrarDano, registrarPasada, leerTabla, leerPredicciones, leerDatosReales };
})();
