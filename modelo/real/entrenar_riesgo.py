"""Modelo de riesgo con DATOS REALES: ¿habrá una alerta crítica del TPMS en los próximos 7 días? (PROP-07)

Los datos reales son alertas (el TPMS solo registra cuando la presión o la temperatura salen de rango);
no traen profundidad de banda ni horas, así que no sirven para el modelo de horas remanentes.
Sí permiten anticipar qué posición de qué equipo está por tener una alerta crítica (nivel 3).

1. Arma un ejemplo por equipo, posición y día con el historial de alertas de los 14 días previos.
2. Objetivo: al menos una alerta de nivel 3 en los 7 días siguientes.
3. Evalúa con corte por fecha (entrena antes de FECHA_CORTE, prueba después) contra una regla simple:
   «más alertas en los últimos 14 días, más riesgo».
4. Reentrena con todo y estima el riesgo actual de cada posición; SHAP entrega las 3 causas principales.
5. Escribe `riesgo_versiones` y `riesgo_posiciones` con origen = 'real'.

Uso:
    python modelo/real/entrenar_riesgo.py            # lee y escribe en Supabase (requiere service_role)
    python modelo/real/entrenar_riesgo.py --prueba   # usa los CSV de modelo/datos/reales/ y no escribe
"""
import argparse
import datetime as dt
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import shap
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.metrics import brier_score_loss, roc_auc_score

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from terreno.supabase_api import Supabase, RAIZ  # noqa: E402

DATOS = RAIZ / "modelo" / "datos" / "reales"
HORIZONTE = 7          # días hacia adelante
HISTORIA = 14          # días hacia atrás
FECHA_CORTE = "2026-04-01"
RIESGO_MEDIO = 0.15   # ≈ 2 veces la tasa base de la prueba (7 %)
RIESGO_ALTO = 0.40    # ≈ 5 veces la tasa base
SIN_ALERTA = 365       # «días desde la última alerta» cuando no hubo ninguna
VARIABLES = {
    "alertas_14d": "Alertas en los últimos 14 días",
    "alertas_3d": "Alertas en los últimos 3 días",
    "criticas_14d": "Alertas críticas en los últimos 14 días",
    "criticas_90d": "Alertas críticas en los últimos 90 días",
    "baja_presion_14d": "Alertas de baja presión (14 días)",
    "alta_presion_14d": "Alertas de alta presión (14 días)",
    "temperatura_14d": "Alertas de temperatura (14 días)",
    "dias_ultima_alerta": "Días desde la última alerta",
    "dias_ultima_critica": "Días desde la última alerta crítica",
    "equipo_alertas_14d": "Alertas del equipo completo (14 días)",
    "posicion_delantera": "Posición delantera",
    "es_cargador": "Equipo cargador",
}


def cargar(prueba):
    if prueba:
        return pd.read_csv(DATOS / "alertas_tpms.csv")
    return pd.DataFrame(Supabase().leer("alertas_tpms", "equipo,tipo_equipo,posicion,tipo_alerta,nivel,fecha_hora",
                                        "&origen=eq.real"))


def ejemplos(a):
    """Un ejemplo por equipo, posición y día, desde la primera alerta del equipo hasta el último día con datos."""
    a = a.copy()
    a["dia"] = pd.to_datetime(a.fecha_hora).dt.normalize()
    a["critica"] = (a.nivel == 3).astype(int)
    a["baja"] = a.tipo_alerta.str.startswith("Baja").astype(int) | a.tipo_alerta.str.contains("baja en").astype(int)
    a["alta"] = a.tipo_alerta.str.startswith("Alta presión").astype(int) | a.tipo_alerta.str.contains("alta en").astype(int)
    a["temp"] = a.tipo_alerta.str.contains("temperatura").astype(int)
    diario = (a.groupby(["equipo", "posicion", "dia"])
               .agg(n=("nivel", "size"), crit=("critica", "sum"), baja=("baja", "sum"), alta=("alta", "sum"),
                    temp=("temp", "sum")).reset_index())
    fin = a.dia.max()
    tipo = a.groupby("equipo").tipo_equipo.first()
    inicio = a.groupby("equipo").dia.min()

    partes = []
    for (eq, pos), g in diario.groupby(["equipo", "posicion"]):
        dias = pd.date_range(inicio[eq], fin, freq="D")
        s = g.set_index("dia").reindex(dias, fill_value=0)[["n", "crit", "baja", "alta", "temp"]]
        rodar = lambda col, k: s[col].rolling(k, min_periods=1).sum()
        e = pd.DataFrame({
            "equipo": eq, "posicion": pos, "dia": dias,
            "alertas_14d": rodar("n", HISTORIA), "alertas_3d": rodar("n", 3),
            "criticas_14d": rodar("crit", HISTORIA), "criticas_90d": rodar("crit", 90),
            "baja_presion_14d": rodar("baja", HISTORIA), "alta_presion_14d": rodar("alta", HISTORIA),
            "temperatura_14d": rodar("temp", HISTORIA),
        })
        idx = np.arange(len(s))
        ult = pd.Series(np.where(s.n.values > 0, idx, np.nan)).ffill().values
        ultc = pd.Series(np.where(s.crit.values > 0, idx, np.nan)).ffill().values
        e["dias_ultima_alerta"] = np.nan_to_num(idx - ult, nan=SIN_ALERTA).clip(max=SIN_ALERTA)
        e["dias_ultima_critica"] = np.nan_to_num(idx - ultc, nan=SIN_ALERTA).clip(max=SIN_ALERTA)
        # objetivo: alguna alerta crítica en los días t+1 … t+HORIZONTE
        futuro = s.crit[::-1].rolling(HORIZONTE, min_periods=1).sum()[::-1].shift(-1)
        e["objetivo"] = (futuro.values > 0).astype(float)
        e.loc[e.dia > fin - pd.Timedelta(days=HORIZONTE), "objetivo"] = np.nan   # futuro aún no observado
        partes.append(e)
    x = pd.concat(partes, ignore_index=True)
    x["equipo_alertas_14d"] = x.groupby(["equipo", "dia"]).alertas_14d.transform("sum") - x.alertas_14d
    x["posicion_delantera"] = (x.posicion <= 2).astype(int)
    x["es_cargador"] = (x.equipo.map(tipo) == "cargador").astype(int)
    x["tipo_equipo"] = x.equipo.map(tipo)
    return x, fin


def modelo():
    return HistGradientBoostingClassifier(max_iter=300, learning_rate=0.05, max_leaf_nodes=15,
                                          min_samples_leaf=80, l2_regularization=1.0, random_state=42)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--prueba", action="store_true", help="usa los CSV locales y no escribe en Supabase")
    args = ap.parse_args()

    a = cargar(args.prueba)
    if a.empty:
        sys.exit("No hay alertas reales cargadas: ejecute antes modelo/real/cargar_reales.py")
    x, fin = ejemplos(a)
    cols = list(VARIABLES)
    con = x[x.objetivo.notna()]
    tr, te = con[con.dia < FECHA_CORTE], con[con.dia >= FECHA_CORTE]

    m = modelo().fit(tr[cols], tr.objetivo)
    p = m.predict_proba(te[cols])[:, 1]
    auc_m = roc_auc_score(te.objetivo, p)
    auc_r = roc_auc_score(te.objetivo, te.alertas_14d)
    tasa = te.objetivo.mean()
    # de cada 10 avisos del modelo, ¿cuántos aciertan? (el 5 % de días-posición con más riesgo)
    corte = np.quantile(p, 0.95)
    precision_top5 = te.objetivo[p >= corte].mean()
    captura_top5 = te.objetivo[p >= corte].sum() / te.objetivo.sum()
    metricas = {"brier_modelo": round(brier_score_loss(te.objetivo, p), 4),
                "brier_tasa_base": round(brier_score_loss(te.objetivo, np.full(len(te), tr.objetivo.mean())), 4),
                "precision_5pct_mayor_riesgo": round(float(precision_top5), 4),
                "criticas_capturadas_5pct": round(float(captura_top5), 4),
                "ejemplos_entrenamiento": int(len(tr)), "ejemplos_prueba": int(len(te)),
                "horizonte_dias": HORIZONTE, "historia_dias": HISTORIA}
    print(f"Ejemplos: {len(con)} (entrenamiento {len(tr)} · prueba {len(te)} desde {FECHA_CORTE})")
    print(f"Tasa base en prueba: {tasa:.3f} · AUC modelo {auc_m:.3f} vs regla simple {auc_r:.3f}")
    print(f"Brier {metricas['brier_modelo']} vs {metricas['brier_tasa_base']} · 5 % de mayor riesgo: "
          f"precisión {precision_top5:.2f}, captura {captura_top5:.2f} de las alertas críticas")

    # Reentrenar con todo y estimar el riesgo de hoy por posición activa en los últimos 180 días
    final = modelo().fit(con[cols], con.objetivo)
    hoy = x[x.dia == fin]
    activos = x[(x.dia > fin - pd.Timedelta(days=180)) & (x.alertas_3d > 0)][["equipo", "posicion"]].drop_duplicates()
    hoy = hoy.merge(activos, on=["equipo", "posicion"]).reset_index(drop=True)
    prob = final.predict_proba(hoy[cols])[:, 1]

    expl = shap.TreeExplainer(final)          # contribuciones en log-odds de la alerta crítica
    sv = expl.shap_values(hoy[cols])
    glob = expl.shap_values(con[cols].sample(5000, random_state=2))
    importancia = dict(zip([VARIABLES[c] for c in cols], np.round(np.abs(glob).mean(0), 4).tolist()))

    version = f"gb-riesgo-{dt.date.today():%Y%m%d}"
    filas = []
    for i, r in hoy.iterrows():
        orden = np.argsort(-np.abs(sv[i]))[:3]
        total = np.abs(sv[i]).sum() or 1
        causas = [{"variable": cols[j], "etiqueta": VARIABLES[cols[j]],
                   "valor": float(r[cols[j]]), "efecto": "aumenta" if sv[i, j] > 0 else "reduce",
                   "peso_pct": round(float(abs(sv[i, j]) / total * 100), 1)} for j in orden]
        pr = float(prob[i])
        filas.append({"modelo_version": version, "equipo": r.equipo, "tipo_equipo": r.tipo_equipo,
                      "posicion": int(r.posicion), "fecha_referencia": fin.strftime("%Y-%m-%d"),
                      "probabilidad": round(pr, 4),
                      "nivel_riesgo": "alto" if pr >= RIESGO_ALTO else "medio" if pr >= RIESGO_MEDIO else "bajo",
                      "alertas_14d": int(r.alertas_14d), "causas": causas})
    niveles = pd.Series([f["nivel_riesgo"] for f in filas]).value_counts().to_dict()
    print(f"Riesgo al {fin:%d-%m-%Y}: {len(filas)} posiciones activas · {niveles}")

    ver = {"version": version, "objetivo": f"Alerta crítica del TPMS (nivel 3) en los próximos {HORIZONTE} días",
           "datos_desde": pd.to_datetime(a.fecha_hora).min().strftime("%Y-%m-%d"),
           "datos_hasta": fin.strftime("%Y-%m-%d"), "fecha_corte": FECHA_CORTE,
           "n_ejemplos": int(len(con)), "tasa_base": round(float(tasa), 4),
           "auc_modelo": round(float(auc_m), 4), "auc_referencia": round(float(auc_r), 4),
           "metricas": metricas, "importancia": importancia}

    if args.prueba:
        DATOS.mkdir(parents=True, exist_ok=True)
        (DATOS / "riesgo_version.json").write_text(json.dumps(ver, ensure_ascii=False, indent=2), encoding="utf-8")
        pd.DataFrame(filas).to_csv(DATOS / "riesgo_posiciones.csv", index=False)
        print(f"Modo prueba: resultados en {DATOS}")
        return
    db = Supabase()
    if db.modo_prueba:
        sys.exit("Falta SUPABASE_SERVICE_ROLE_KEY para escribir en la base.")
    db.insertar("riesgo_versiones", [ver], conflicto="version")
    db.insertar("riesgo_posiciones", filas, conflicto="modelo_version,equipo,posicion")
    print(f"Publicado {version} en Supabase.")


if __name__ == "__main__":
    main()
