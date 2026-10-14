"""Genera docs/seed.sql a partir de los datos iniciales del prototipo (src/index.html).

Así la base de Supabase y el modo sin conexión del prototipo parten de los mismos
67 camiones, 402 neumáticos, daños y órdenes de trabajo.

Uso (desde la raíz del repositorio):
    python scripts/generar_seed.py
"""
import json
import re
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
HTML = (RAIZ / "src" / "index.html").read_text(encoding="utf-8")
SALIDA = RAIZ / "docs" / "seed.sql"


def bloque(nombre, cierre, claves_js=False):
    """Extrae el literal JS de `const NOMBRE = ...;` y lo convierte a JSON."""
    m = re.search(rf"const {nombre} = (.*?\n\s*{re.escape(cierre)});", HTML, re.S)
    if not m:
        raise SystemExit(f"No se encontró {nombre} en src/index.html")
    txt = re.sub(r"//[^\n]*", "", m.group(1))           # quitar comentarios
    if claves_js:  # objetos JS con claves sin comillas
        txt = re.sub(r"([{,]\s*)([A-Za-z_]\w*)\s*:", r'\1"\2":', txt)
    return json.loads(txt)


TRUCKS = bloque("INITIAL_TRUCKS", "]")
KNOWN = bloque("INITIAL_KNOWN_TIRES", "}")
DAMAGES = bloque("INITIAL_DAMAGES", "}")
ORDERS = bloque("INITIAL_ORDERS", "]")
WINDOWS = bloque("INITIAL_WINDOWS", "]", claves_js=True)


def q(v):
    if v is None:
        return "NULL"
    if isinstance(v, bool):
        return "TRUE" if v else "FALSE"
    if isinstance(v, (int, float)):
        return str(v)
    return "'" + str(v).replace("'", "''") + "'"


def fecha_iso(ddmmyyyy):
    d, m, y = ddmmyyyy.split(" ")[0].split("-")
    return f"{y}-{m}-{d}"


def zona(h):
    return "gris" if h is None else "rojo" if h < 200 else "amarillo" if h < 500 else "verde"


def valores(filas):
    return ",\n".join("(" + ", ".join(q(v) for v in f) + ")" for f in filas)


# --- Neumáticos y mediciones (misma lógica que getTires() en el prototipo) ---
camiones, neumaticos, mediciones, danos = [], [], [], []
n_med = 3000
for ci, (codigo, modelo, horometro, horas) in enumerate(TRUCKS):
    num = codigo.split("-")[1]
    camiones.append((codigo, modelo or "Cat 793F", int(horometro.replace(".", "").replace(" h", "") or 15000)))
    for k, h in enumerate(horas):
        p = k + 1
        key = f"{num}-{p}"
        kn = KNOWN.get(key)
        rate = kn[2] if kn else 1.1
        mm = kn[1] if kn else round(20 + h * rate / 100, 1)
        temp = (kn[4] if len(kn) > 4 else 76) if kn else 74 + ((p * 3 + ci * 2) % 18)
        serial = kn[0] if kn else f"5980R63-{2000 + ci * 137 + p * 53}-{1300 + ci * 61 + p * 17}"
        fecha = fecha_iso(kn[3]) if kn else "2026-09-24"
        neumaticos.append((serial, codigo, p))
        n_med += 1
        med = f"med-{n_med}"
        mediciones.append((med, serial, f"{fecha} 08:00-03", camiones[-1][2], mm, rate,
                           "observada" if h < 500 else "nominal", temp, h, zona(h)))
        d = DAMAGES.get(key)
        if d:
            danos.append((med, serial, str(d[0]), d[1], d[2]))

# Neumáticos de órdenes históricas que ya no están montados en la flota
montados = {n[0] for n in neumaticos}
desmontados = sorted({o[2] for o in ORDERS} - montados)

# Ventanas: las 3 ofertadas en el prototipo + las ventanas que usan las órdenes existentes
ventanas = [(w["id"], fecha_iso(w["dia"]), w["turno"], w["max"], w["libres"], w["en"], True) for w in WINDOWS]
clave_ventana = {(w[1], w[2]): w[0] for w in ventanas}
for o in ORDERS:
    k = (fecha_iso(o[5]), o[6])
    if k not in clave_ventana:
        nid = len(ventanas) + 1
        clave_ventana[k] = nid
        ventanas.append((nid, k[0], k[1], 3, 2, 0, False))

ordenes, historial = [], []
for o in ORDERS:
    cod, emision, serial, tipo, nota, dia, turno, horas_em, med, origen, estado, hist = o
    d, hora = emision.split(" ")
    ordenes.append((cod, f"{fecha_iso(d)} {hora}-03", serial, clave_ventana[(fecha_iso(dia), turno)],
                    tipo, nota, horas_em, med, origen, estado))
    for linea in hist:
        partes = [x.strip() for x in linea.split("·")]
        fh, hh = partes[0].split(" ")
        historial.append((cod, f"{fecha_iso(fh)} {hh}-03", partes[1], "creacion", " · ".join(partes[2:])))

SQL = f"""-- =============================================================================
-- DATOS DE DEMOSTRACIÓN (SEED) · CONTROL DE NEUMÁTICOS CAEX
-- Generado por scripts/generar_seed.py a partir de src/index.html. No editar a mano.
-- Ejecutar en el SQL Editor de Supabase DESPUÉS de docs/schema.sql.
-- ATENCIÓN: borra todos los datos y los reemplaza por la flota de demostración
-- ({len(camiones)} camiones, {len(neumaticos)} neumáticos montados).
-- =============================================================================

BEGIN;

TRUNCATE historial_ordenes, ordenes_trabajo, danos_neumaticos, mediciones,
         neumaticos, camiones, ventanas_taller RESTART IDENTITY CASCADE;

INSERT INTO camiones (codigo, modelo, horometro_h) VALUES
{valores(camiones)};

INSERT INTO neumaticos (serial, caex_id, posicion)
SELECT v.serial, c.id, v.posicion
FROM (VALUES
{valores(neumaticos)}
) AS v(serial, caex, posicion)
JOIN camiones c ON c.codigo = v.caex;

-- Neumáticos ya retirados que siguen referenciados por órdenes históricas
INSERT INTO neumaticos (serial, caex_id, posicion) VALUES
{valores([(s, None, None) for s in desmontados])};

INSERT INTO mediciones (codigo_medicion, neumatico_id, fecha_pasada, horas_operacion, profundidad_mm,
                        tasa_desgaste_por_100h, tipo_tasa, temperatura_flanco_c,
                        horas_remanentes_calculadas, zona_calculada)
SELECT v.cod, n.id, v.fecha::timestamptz, v.horas_op, v.mm, v.tasa, v.tipo, v.temp, v.rem, v.zona::zona_criticidad_enum
FROM (VALUES
{valores(mediciones)}
) AS v(cod, serial, fecha, horas_op, mm, tasa, tipo, temp, rem, zona)
JOIN neumaticos n ON n.serial = v.serial;

INSERT INTO danos_neumaticos (medicion_id, neumatico_id, severidad, descripcion, confianza_ia)
SELECT m.id, n.id, v.sev::severidad_dano_enum, v.descr, v.conf
FROM (VALUES
{valores(danos)}
) AS v(med, serial, sev, descr, conf)
JOIN neumaticos n ON n.serial = v.serial
JOIN mediciones m ON m.codigo_medicion = v.med;

INSERT INTO ventanas_taller (id, dia, turno, cupos_totales, cupos_libres, horas_hasta_ventana, reservable) VALUES
{valores(ventanas)};
SELECT setval('ventanas_taller_id_seq', (SELECT max(id) FROM ventanas_taller));

-- Las órdenes históricas ya consumieron su cupo: se cargan sin disparar el descuento.
ALTER TABLE ordenes_trabajo DISABLE TRIGGER trg_decrementar_cupo;

INSERT INTO ordenes_trabajo (codigo, fecha_emision, neumatico_id, ventana_id, tipo_intervencion,
                             justificacion_nota, horas_remanentes_emision, medicion_codigo,
                             origen_detalle, estado)
SELECT v.cod, v.emision::timestamptz, n.id, v.ventana, v.tipo::tipo_intervencion_enum, v.nota,
       v.horas, v.med, v.origen, v.estado::estado_orden_enum
FROM (VALUES
{valores(ordenes)}
) AS v(cod, emision, serial, ventana, tipo, nota, horas, med, origen, estado)
JOIN neumaticos n ON n.serial = v.serial;

ALTER TABLE ordenes_trabajo ENABLE TRIGGER trg_decrementar_cupo;

INSERT INTO historial_ordenes (orden_id, fecha_evento, autor, accion, motivo)
SELECT o.id, v.fecha::timestamptz, v.autor, v.accion, v.motivo
FROM (VALUES
{valores(historial)}
) AS v(orden, fecha, autor, accion, motivo)
JOIN ordenes_trabajo o ON o.codigo = v.orden;

COMMIT;

-- Verificación rápida (debe mostrar {len(camiones)} · {len(neumaticos) + len(desmontados)} · {len(ordenes)}):
SELECT (SELECT count(*) FROM camiones) AS camiones,
       (SELECT count(*) FROM neumaticos) AS neumaticos,
       (SELECT count(*) FROM ordenes_trabajo) AS ordenes;
"""

SALIDA.write_text(SQL, encoding="utf-8")
print(f"{SALIDA.relative_to(RAIZ)}: {len(camiones)} camiones, {len(neumaticos)} neumáticos montados, "
      f"{len(desmontados)} desmontados, {len(danos)} daños, {len(ventanas)} ventanas, {len(ordenes)} órdenes")
