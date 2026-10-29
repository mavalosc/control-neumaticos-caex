"""Carga en Supabase las alertas TPMS y los excesos de velocidad REALES, anonimizados (PROP-07).

Entrada: el Excel consolidado que exporta el sistema de monitoreo de la faena
(hojas «Alertas neumáticos» y «Eventos velocidad»). El Excel nunca entra al repositorio.

1. Descarta los duplicados exactos que marca el propio Excel y los equipos de prueba.
2. Anonimiza: cada equipo pasa a «Camión A», «Cargador B»… y cada sensor a «S-001»…
   Los mensajes del TPMS (que nombran al equipo) no se guardan; solo tipo, nivel, valor y límite.
3. Escribe `alertas_tpms` y `eventos_velocidad` con origen = 'real' (idempotente por `clave`).
4. Guarda la tabla de equivalencias SOLO en modelo/datos/reales/ (carpeta ignorada por git).

Uso:
    python modelo/real/cargar_reales.py RUTA_DEL_EXCEL            # escribe en Supabase (requiere service_role)
    python modelo/real/cargar_reales.py RUTA_DEL_EXCEL --prueba   # solo genera los CSV anonimizados
"""
import argparse
import hashlib
import string
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from terreno.supabase_api import Supabase, RAIZ  # noqa: E402

SALIDA = RAIZ / "modelo" / "datos" / "reales"
TIPO_EQUIPO = {"T": "camion", "L": "cargador"}
NOMBRE_TIPO = {"camion": "Camión", "cargador": "Cargador"}


def huella(*valores):
    return hashlib.sha1("|".join(str(v) for v in valores).encode("utf-8")).hexdigest()


def equivalencias(codigos):
    """Asigna letras por orden de código dentro de cada tipo: el primer camión → Camión A, el segundo → Camión B…"""
    filas = []
    for prefijo, tipo in TIPO_EQUIPO.items():
        propios = sorted(c for c in codigos if c[:1] == prefijo)
        for i, c in enumerate(propios):
            letra = string.ascii_uppercase[i] if i < 26 else f"{i + 1}"
            filas.append({"codigo_original": c, "equipo": f"{NOMBRE_TIPO[tipo]} {letra}", "tipo_equipo": tipo})
    return pd.DataFrame(filas)


def leer_alertas(excel):
    a = pd.read_excel(excel, sheet_name="Alertas neumáticos")
    a.columns = ["codigo", "serie_neumatico", "sensor", "prioridad", "posicion", "sistema", "mensaje",
                 "tipo_alerta", "nivel", "fecha_hora", "valor", "turno", "archivo", "duplicado"]
    a = a[(a.duplicado == "No") & a.codigo.str.match(r"^[TL]\d")].copy()
    a["limite"] = a.mensaje.str.extract(r"l[ií]mite (?:de )?([\d.]+)")[0].astype(float)
    a["unidad"] = a.tipo_alerta.str.contains("temperatura", case=False).map({True: "°C", False: "psi"})
    return a


def leer_velocidad(excel):
    v = pd.read_excel(excel, sheet_name="Eventos velocidad")
    v.columns = ["codigo", "fecha", "hora", "velocidad_kmh", "limite_kmh", "area", "turno", "archivo", "duplicado"]
    v = v[(v.duplicado == "No") & v.codigo.str.match(r"^[TL]\d")].copy()
    v["fecha_hora"] = pd.to_datetime(v.fecha.dt.strftime("%Y-%m-%d") + " " + v.hora.astype(str))
    return v


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("excel", type=Path)
    ap.add_argument("--prueba", action="store_true", help="no escribe en Supabase")
    args = ap.parse_args()

    a, v = leer_alertas(args.excel), leer_velocidad(args.excel)
    eq = equivalencias(set(a.codigo) | set(v.codigo))
    sensores = {s: f"S-{i + 1:03d}" for i, s in enumerate(sorted(a.sensor.dropna().unique()))}

    a = a.merge(eq, left_on="codigo", right_on="codigo_original")
    a["sensor"] = a.sensor.map(sensores)
    a["fecha_hora"] = a.fecha_hora.dt.strftime("%Y-%m-%dT%H:%M:%S")
    a["clave"] = [huella(*r) for r in a[["equipo", "posicion", "sensor", "tipo_alerta", "nivel", "fecha_hora", "valor"]].itertuples(index=False)]
    alertas = a.drop_duplicates("clave")[["clave", "equipo", "tipo_equipo", "posicion", "sensor", "tipo_alerta",
                                          "nivel", "valor", "limite", "unidad", "fecha_hora"]]

    v = v.merge(eq, left_on="codigo", right_on="codigo_original")
    v["fecha_hora"] = v.fecha_hora.dt.strftime("%Y-%m-%dT%H:%M:%S")
    v["area"] = v.area.where(v.area.notna(), None)
    v["clave"] = [huella(*r) for r in v[["equipo", "fecha_hora", "velocidad_kmh", "limite_kmh", "area"]].itertuples(index=False)]
    velocidad = v.drop_duplicates("clave")[["clave", "equipo", "tipo_equipo", "fecha_hora", "velocidad_kmh", "limite_kmh", "area"]]

    SALIDA.mkdir(parents=True, exist_ok=True)
    eq.to_csv(SALIDA / "equivalencias.csv", index=False)   # SOLO local: permite volver al código original
    alertas.to_csv(SALIDA / "alertas_tpms.csv", index=False)
    velocidad.to_csv(SALIDA / "eventos_velocidad.csv", index=False)
    print(f"Equipos: {len(eq)} ({(eq.tipo_equipo == 'camion').sum()} camiones, {(eq.tipo_equipo == 'cargador').sum()} cargadores) · "
          f"sensores: {len(sensores)}")
    print(f"Alertas TPMS: {len(alertas)} ({alertas.fecha_hora.min()[:10]} a {alertas.fecha_hora.max()[:10]}) · "
          f"excesos de velocidad: {len(velocidad)} ({velocidad.fecha_hora.min()[:10]} a {velocidad.fecha_hora.max()[:10]})")

    if args.prueba:
        print(f"Modo prueba: CSV anonimizados en {SALIDA}")
        return
    db = Supabase()
    if db.modo_prueba:
        sys.exit("Falta SUPABASE_SERVICE_ROLE_KEY (Secrets de GitHub o .env local) para escribir en la base.")
    limpiar = lambda df: [{k: (None if pd.isna(x) else x) for k, x in r.items()} for r in df.to_dict("records")]
    db.insertar("alertas_tpms", limpiar(alertas), conflicto="clave")
    db.insertar("eventos_velocidad", limpiar(velocidad), conflicto="clave")
    print("Cargado en Supabase (las filas ya existentes se omiten).")


if __name__ == "__main__":
    main()
