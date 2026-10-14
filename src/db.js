// Capa de datos del prototipo: lee y escribe en Supabase y entrega a las pantallas
// el mismo objeto `state` que usa el modo local (localStorage).
// Requiere: config.js (window.CAEX_CONFIG) y supabase-js v2 cargado desde CDN.
(function () {
  const cfg = window.CAEX_CONFIG || {};
  const cliente = cfg.SUPABASE_URL && cfg.SUPABASE_ANON_KEY && window.supabase
    ? window.supabase.createClient(cfg.SUPABASE_URL, cfg.SUPABASE_ANON_KEY)
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
  const ACCION = { modificacion: "modificación de orden", anulacion: "orden anulada" };

  function revisar({ data, error }) {
    if (error) throw new Error(error.message);
    return data;
  }

  async function cargar() {
    const [vista, ventanas, ordenes] = await Promise.all([
      cliente.from("vista_tablero_turno").select("*").order("caex_codigo").order("posicion").limit(5000).then(revisar),
      cliente.from("ventanas_taller").select("*").eq("reservable", true).order("dia").order("id").then(revisar),
      cliente.from("ordenes_trabajo")
        .select("id,codigo,fecha_emision,tipo_intervencion,justificacion_nota,horas_remanentes_emision,medicion_codigo,origen_detalle,estado,neumaticos(serial),ventanas_taller(id,dia,turno),historial_ordenes(fecha_evento,autor,accion,motivo)")
        .order("fecha_emision", { ascending: false }).then(revisar)
    ]);
    if (!vista.length) throw new Error("La base no tiene neumáticos. Ejecuta docs/seed.sql en Supabase.");

    const trucks = [], knownTires = {}, damages = {};
    const porCamion = new Map();
    vista.forEach(r => {
      if (!porCamion.has(r.caex_codigo)) {
        const camion = [r.caex_codigo, r.caex_modelo, Number(r.horometro_h).toLocaleString("es-CL") + " h", [null, null, null, null, null, null]];
        porCamion.set(r.caex_codigo, camion);
        trucks.push(camion);
      }
      const key = r.caex_codigo.split("-")[1] + "-" + r.posicion;
      porCamion.get(r.caex_codigo)[3][r.posicion - 1] = r.horas_remanentes_calculadas;
      knownTires[key] = [r.neumatico_serial, Number(r.profundidad_mm), Number(r.tasa_desgaste_por_100h),
        r.fecha_pasada ? fechaCL(r.fecha_pasada) : "sin pasada", Number(r.temperatura_flanco_c)];
      const nivel = Number(r.nivel_dano);
      if (nivel > 0) damages[key] = [nivel, r.detalle_dano, r.confianza_ia == null ? 1 : Number(r.confianza_ia)];
      idNeumatico[r.neumatico_serial] = r.neumatico_id;
      ultimaMedicion[r.neumatico_serial] = r.codigo_medicion;
    });

    const orders = ordenes.map(o => {
      idOrden[o.codigo] = o.id;
      const hist = (o.historial_ordenes || [])
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

    return { trucks, knownTires, damages, orders, windows };
  }

  async function historial(codigo, accion, motivo) {
    revisar(await cliente.from("historial_ordenes").insert({ orden_id: idOrden[codigo], autor: "planificador", accion, motivo }));
  }

  async function emitirOrden({ codigo, serial, ventanaId, tipo, nota, horas, origen }) {
    const fila = revisar(await cliente.from("ordenes_trabajo").insert({
      codigo, neumatico_id: idNeumatico[serial], ventana_id: ventanaId, tipo_intervencion: tipo,
      justificacion_nota: nota, horas_remanentes_emision: horas, medicion_codigo: ultimaMedicion[serial] || null,
      origen_detalle: origen, estado: "programada"
    }).select("id").single());
    idOrden[codigo] = fila.id;
    await historial(codigo, "creacion", "orden emitida y sincronizada con ERP");
  }

  async function modificarOrden(codigo, { ventanaId, nota, motivo }) {
    const cambios = { justificacion_nota: nota, actualizado_en: new Date().toISOString() };
    if (ventanaId) cambios.ventana_id = ventanaId;
    revisar(await cliente.from("ordenes_trabajo").update(cambios).eq("codigo", codigo));
    await historial(codigo, "modificacion", motivo);
  }

  async function anularOrden(codigo, motivo) {
    revisar(await cliente.from("ordenes_trabajo").update({ estado: "anulada", actualizado_en: new Date().toISOString() }).eq("codigo", codigo));
    await historial(codigo, "anulacion", motivo);
  }

  async function registrarDano(serial, nivel, descripcion) {
    revisar(await cliente.from("danos_neumaticos").insert({
      neumatico_id: idNeumatico[serial], severidad: String(nivel), descripcion: nivel > 0 ? descripcion : "Sin daño",
      confianza_ia: 1, validado_por_humano: true, usuario_validador: "planificador"
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

  window.DB = { activo: !!cliente, cargar, emitirOrden, modificarOrden, anularOrden, registrarDano, registrarPasada };
})();
