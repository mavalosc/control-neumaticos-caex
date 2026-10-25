"""Entrena el modelo de desgaste con los datos de terreno SIMULADOS y publica predicciones (PROP-06).

1. Lee `ciclos_operacion` (origen = 'simulado') y arma ventanas de VENTANA días por neumático y vida.
2. Evalúa Gradient Boosting en camiones no vistos (20 %) contra el promedio de flota.
3. Reentrena con todos los datos y predice la tasa de desgaste de cada neumático con las
   condiciones de su última ventana.
4. Horas remanentes del modelo = (profundidad de la última medición del pórtico − 20 mm) ÷ tasa × 100.
5. SHAP: las 3 variables que más pesan en la predicción de cada neumático.
6. Escribe `modelo_versiones` y `predicciones_modelo` con origen = 'simulado'.

Uso:
    python modelo/terreno/entrenar_terreno.py            # escribe en Supabase (requiere service_role)
    python modelo/terreno/entrenar_terreno.py --prueba   # usa modelo/datos/terreno_ciclos.csv y guarda CSV
"""
import argparse
import datetime as dt
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import shap
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.model_selection import GroupShuffleSplit

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import generar_datos as G  # noqa: E402
from terreno.supabase_api import Supabase, RAIZ  # noqa: E402

VENTANA = 10   # días (≈ 190 h): el ruido del pórtico (±0,25 mm) no domina la tasa observada
VARIABLES = {
    "presion_desv_pct": "Presión de inflado",
    "temp_neumatico_c": "Temperatura del neumático",
    "profundidad_inicio_mm": "Profundidad remanente",
    "carga_t": "Carga transportada",
    "velocidad_kmh": "Velocidad de operación",
    "distancia_km": "Distancia recorrida",
    "horas_vida": "Horas de uso",
    "frac_roca_suelta": "Terreno de roca suelta",
    "frac_barro": "Terreno con barro",
    "pendiente_pct": "Pendiente de la ruta",
    "posicion_delantera": "Posición delantera",
    "frenadas_por_h": "Frenadas y aceleraciones",
    "temp_ambiente_c": "Temperatura ambiente",
    "tkph": "TKPH (carga × velocidad)",
}
NUMERICAS = ["presion_desv_pct", "temp_neumatico_c", "carga_t", "velocidad_kmh", "pendiente_pct",
             "frenadas_por_h", "temp_ambiente_c", "tkph", "tasa_real_simulada"]


def ventanas(c):
    """Agrupa días consecutivos de cada neumático y vida en ventanas de VENTANA días."""
    c = c.sort_values(["neumatico_id", "vida", "ciclo"]).copy()
    c["v"] = (c.ciclo - 1) // VENTANA
    c["roca"] = (c.terreno == "roca_suelta").astype(float)
    c["barro"] = (c.terreno == "barro").astype(float)
    for k in NUMERICAS + ["roca", "barro"]:
        c[k + "_w"] = c[k] * c.horas_ciclo
    g = c.groupby(["neumatico_id", "vida", "v"], sort=False)
    a = g.agg(serial=("serial", "first"), caex=("caex_codigo", "first"), posicion=("posicion", "first"),
              horas=("horas_ciclo", "sum"), distancia_km=("distancia_km", "sum"), horas_vida=("horas_vida", "first"),
              profundidad_inicio_mm=("profundidad_mm", "first"), profundidad_fin_mm=("profundidad_mm", "last"),
              primer_ciclo=("ciclo", "first"), n=("ciclo", "size"), fecha_fin=("fecha", "last"),
              **{k: (k + "_w", "sum") for k in NUMERICAS + ["roca", "barro"]})
    for k in NUMERICAS + ["roca", "barro"]:
        a[k] = a[k] / a.horas
    a = a.reset_index().rename(columns={"roca": "frac_roca_suelta", "barro": "frac_barro"})
    a["distancia_km"] = a.distancia_km / a.n
    a["posicion_delantera"] = (a.posicion <= 2).astype(float)
    # tasa observada: caída de la profundidad medida entre el inicio y el fin de la ventana
    a["tasa_obs"] = (a.profundidad_inicio_mm - a.profundidad_fin_mm) / (a.horas * (a.n - 1) / a.n) * 100
    return a


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--prueba", action="store_true", help="usa el CSV del generador y no escribe en Supabase")
    args = ap.parse_args()
    sb = Supabase()
    prueba = args.prueba or sb.modo_prueba

    columnas = ("neumatico_id,serial,caex_codigo,posicion,vida,ciclo,fecha,horas_ciclo,horas_vida,presion_desv_pct,"
                "temp_neumatico_c,temp_ambiente_c,carga_t,velocidad_kmh,distancia_km,terreno,pendiente_pct,"
                "frenadas_por_h,tkph,profundidad_mm,tasa_real_simulada")
    if prueba:
        c = pd.read_csv(RAIZ / "modelo" / "datos" / "terreno_ciclos.csv")
    else:
        c = pd.DataFrame(sb.leer("ciclos_operacion", columnas, filtros="&origen=eq.simulado"))
    if c.empty:
        raise SystemExit("No hay ciclos de terreno: ejecute primero generar_terreno.py")
    c = c[columnas.split(",")].copy()
    for k in c.columns:
        if k not in ("neumatico_id", "serial", "caex_codigo", "terreno", "fecha"):
            c[k] = pd.to_numeric(c[k])

    w = ventanas(c)
    completas = w[(w.n == VENTANA) & (w.tasa_obs > 0.05)]
    X, y = completas[list(VARIABLES)], np.log(completas.tasa_obs)

    # evaluación en camiones no vistos
    tr, te = next(GroupShuffleSplit(n_splits=1, test_size=0.2, random_state=7).split(completas, groups=completas.caex))
    gb = HistGradientBoostingRegressor(max_iter=400, learning_rate=0.05, max_leaf_nodes=31, random_state=7)
    gb.fit(X.iloc[tr], y.iloc[tr])
    real = completas.tasa_real_simulada.iloc[te]
    mae_modelo = float(np.abs(np.exp(gb.predict(X.iloc[te])) - real).mean())
    mae_promedio = float(np.abs(completas.tasa_obs.iloc[tr].mean() - real).mean())

    # modelo final con todos los datos
    gb.fit(X, y)
    ultimas = (w.sort_values(["neumatico_id", "vida", "v"]).groupby("neumatico_id").tail(1))
    flota = pd.DataFrame(sb.leer("vista_tablero_turno", "neumatico_id,neumatico_serial,profundidad_mm"))
    flota["profundidad_medicion"] = pd.to_numeric(flota.pop("profundidad_mm"))   # última medición del pórtico
    ultimas = ultimas.merge(flota, on="neumatico_id", how="inner")
    tasa = np.exp(gb.predict(ultimas[list(VARIABLES)]))
    sv = shap.TreeExplainer(gb).shap_values(ultimas[list(VARIABLES)])

    version = "gb-terreno-" + (dt.datetime.utcnow() - dt.timedelta(hours=3)).strftime("%Y%m%d")
    importancia = dict(sorted(((VARIABLES[k], round(float(v), 4)) for k, v in zip(VARIABLES, np.abs(sv).mean(0))),
                              key=lambda x: -x[1]))
    predicciones = []
    for i, fila in enumerate(ultimas.itertuples()):
        aporte = sv[i]
        total = np.abs(aporte).sum() or 1
        top = np.argsort(-np.abs(aporte))[:3]
        causas = [{"variable": list(VARIABLES)[j], "etiqueta": list(VARIABLES.values())[j],
                   "efecto": "aumenta" if aporte[j] > 0 else "reduce",
                   "peso_pct": round(float(abs(aporte[j]) / total * 100), 1)} for j in top]
        horas = max(0, (fila.profundidad_medicion - G.UMBRAL_RETIRO_MM) / tasa[i] * 100)
        predicciones.append({"neumatico_id": fila.neumatico_id, "serial": fila.neumatico_serial, "modelo_version": version,
                             "profundidad_mm": round(float(fila.profundidad_medicion), 2),
                             "tasa_prevista_mm_100h": round(float(tasa[i]), 3), "horas_remanentes_modelo": int(round(horas)),
                             "causas": causas, "origen": "simulado"})
    registro = {"version": version, "n_ciclos": int(len(c)), "n_ventanas": int(len(completas)),
                "camiones_prueba": int(completas.caex.iloc[te].nunique()), "mae_tasa_modelo": round(mae_modelo, 4),
                "mae_tasa_promedio": round(mae_promedio, 4), "importancia": importancia, "origen": "simulado"}

    print(f"{version}: {len(c):,} ciclos · {len(completas):,} ventanas · MAE tasa en camiones no vistos "
          f"{mae_modelo:.3f} mm/100 h (promedio de flota {mae_promedio:.3f}) · {len(predicciones)} predicciones")
    print("Importancia SHAP:", ", ".join(f"{k} {v}" for k, v in list(importancia.items())[:5]))
    if prueba:
        destino = RAIZ / "modelo" / "datos"
        pd.DataFrame(predicciones).assign(causas=lambda d: d.causas.map(json.dumps)).to_csv(destino / "terreno_predicciones.csv", index=False)
        (destino / "terreno_version.json").write_text(json.dumps(registro, ensure_ascii=False, indent=1), encoding="utf-8")
        print("MODO PRUEBA: no se escribió en Supabase; resultados en modelo/datos/terreno_*")
    else:
        sb.insertar("modelo_versiones", [registro], conflicto="version")
        sb.insertar("predicciones_modelo", predicciones)
        print("versión y predicciones guardadas en Supabase (origen = 'simulado')")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
