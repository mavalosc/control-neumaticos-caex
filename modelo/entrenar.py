"""PoC del modelo de desgaste y vida útil remanente (RUL) de neumáticos OTR.

1. Agrega los ciclos en ventanas de ~200 h (4 pasadas) para que el ruido del pórtico no domine.
2. Modelo de DESGASTE:
   a) Regresión multivariable sobre log(tasa) con indicadores derivados: estima el efecto % de cada variable.
   b) Gradient Boosting sobre las 12 variables en bruto + TKPH, explicado con SHAP.
3. Modelo de DAÑO: supervivencia (Cox) sobre la vida de cada neumático, con censura.
4. Valida las horas remanentes contra el método actual (recta de profundidad vs horas, backend/app/proyeccion.py).
5. Compara los efectos estimados con los efectos VERDADEROS del simulador.

Uso (desde la raíz del repositorio):
    modelo/.venv/Scripts/python modelo/entrenar.py
Salida: modelo/resultados/ (gráficos, metricas.json, REPORTE.md)
"""
import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import shap
from lifelines import CoxPHFitter
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import GroupShuffleSplit

sys.path.insert(0, str(Path(__file__).resolve().parent))
import generar_datos as G  # noqa: E402  (efectos verdaderos y constantes del simulador)

RAIZ = Path(__file__).resolve().parent
DATOS, RES = RAIZ / "datos", RAIZ / "resultados"
RES.mkdir(exist_ok=True)
VENTANA = 4
sys.stdout.reconfigure(encoding="utf-8")

VARIABLES = {  # las 12 variables de la propuesta (+ TKPH como indicador derivado)
    "presion_desv_pct": "Presión de inflado (% vs nominal)",
    "temp_neumatico_c": "Temperatura del neumático (°C)",
    "profundidad_inicio_mm": "Nivel de desgaste: profundidad (mm)",
    "carga_t": "Carga transportada (t)",
    "velocidad_kmh": "Velocidad de operación (km/h)",
    "distancia_km": "Distancia recorrida (km)",
    "horas_vida": "Horas de uso del neumático",
    "frac_roca_suelta": "Terreno: % roca suelta",
    "frac_barro": "Terreno: % barro",
    "pendiente_pct": "Pendiente de la ruta (%)",
    "posicion_delantera": "Posición delantera (P1-P2)",
    "frenadas_por_h": "Frenadas y aceleraciones fuertes (/h)",
    "temp_ambiente_c": "Temperatura ambiente (°C)",
    "tkph": "TKPH (carga x velocidad)",
}


# ---------------------------------------------------------------- 1. ventanas
def ventanas(c):
    c = c.copy()
    c["v"] = (c.ciclo - 1) // VENTANA
    c["presion_baja"] = (-c.presion_desv_pct).clip(lower=0)
    c["presion_alta"] = c.presion_desv_pct.clip(lower=0)
    c["roca"] = (c.terreno == "roca_suelta").astype(float)
    c["barro"] = (c.terreno == "barro").astype(float)
    c["w"] = c.horas_ciclo
    num = ["presion_desv_pct", "presion_baja", "presion_alta", "temp_neumatico_c", "carga_t", "velocidad_kmh",
           "pendiente_pct", "frenadas_por_h", "temp_ambiente_c", "tkph", "roca", "barro", "tasa_real_mm_100h"]
    for k in num:
        c[k + "_w"] = c[k] * c.w
    g = c.groupby(["serial", "v"], sort=False)
    a = g.agg(caex=("caex", "first"), posicion=("posicion", "first"), horas=("w", "sum"),
              distancia_km=("distancia_km", "sum"), horas_vida=("horas_inicio_vida", "first"),
              profundidad_inicio_mm=("profundidad_anterior_mm", "first"),
              profundidad_fin_mm=("profundidad_medida_mm", "last"), n=("ciclo", "size"),
              **{k: (k + "_w", "sum") for k in num})
    for k in num:
        a[k] = a[k] / a.horas
    a = a[a.n == VENTANA].reset_index()
    a = a.rename(columns={"roca": "frac_roca_suelta", "barro": "frac_barro", "tasa_real_mm_100h": "tasa_real"})
    a["distancia_km"] = a.distancia_km / a.horas * 50          # por ciclo de 50 h, comparable
    a["posicion_delantera"] = (a.posicion <= 2).astype(float)
    a["tasa_obs"] = (a.profundidad_inicio_mm - a.profundidad_fin_mm) / a.horas * 100
    return a[a.tasa_obs > 0.05]


# ---------------------------------------------------------------- 2a. regresión con indicadores
INDICADORES = {  # columna -> (nombre, efecto verdadero en log por unidad, unidad)
    "presion_baja": ("Presión bajo nominal", G.VERDAD_DESGASTE["presion_baja_pct"], "por 1 %"),
    "presion_alta": ("Presión sobre nominal", G.VERDAD_DESGASTE["presion_alta_pct"], "por 1 %"),
    "log_tkph": ("TKPH", G.VERDAD_DESGASTE["tkph_rel"], "por +10 % de TKPH"),
    "frac_roca_suelta": ("Terreno roca suelta", G.VERDAD_DESGASTE["terreno_roca_suelta"], "vs compactado"),
    "frac_barro": ("Terreno barro", G.VERDAD_DESGASTE["terreno_barro"], "vs compactado"),
    "pendiente_pct": ("Pendiente", G.VERDAD_DESGASTE["pendiente_pct"], "por punto (bajo 6 %)"),
    "posicion_delantera": ("Posición delantera", G.VERDAD_DESGASTE["posicion_delantera"], "vs trasera"),
    "frenadas_por_h": ("Frenadas fuertes", G.VERDAD_DESGASTE["frenadas_por_h"], "por frenada/h"),
    "temp_ambiente_c": ("Temperatura ambiente", G.VERDAD_DESGASTE["temp_ambiente_c"], "por °C"),
    "temp_neumatico_c": ("Temperatura del neumático", 0.0, "por °C (es consecuencia, no causa)"),
    "horas_vida": ("Horas de uso", 0.0, "por hora"),
    "profundidad_inicio_mm": ("Profundidad remanente", 0.0, "por mm"),
}


def matriz_indicadores(d):
    x = d[[k for k in INDICADORES if k != "log_tkph"]].copy()
    x["log_tkph"] = np.log(d.tkph / G.TKPH_REFERENCIA)
    return x[list(INDICADORES)]


# ---------------------------------------------------------------- 4. RUL
def rul_en_punto(c, modelo_gb, umbral_punto):
    """Para cada vida terminada por desgaste: horas remanentes reales vs estimadas cuando la
    profundidad MEDIDA cruza `umbral_punto`."""
    filas = []
    for serial, v in c.groupby("serial", sort=False):
        v = v.sort_values("ciclo")
        idx = np.argmax(v.profundidad_medida_mm.values <= umbral_punto)
        if v.profundidad_medida_mm.values[idx] > umbral_punto or idx < 2 * VENTANA:
            continue
        hasta = v.iloc[: idx + 1]
        h_ahora = hasta.horas_inicio_vida.iloc[-1] + hasta.horas_ciclo.iloc[-1]
        d_ahora = hasta.profundidad_medida_mm.iloc[-1]
        h_total = v.horas_inicio_vida.iloc[-1] + v.horas_ciclo.iloc[-1]
        real = h_total - h_ahora
        # (a) método actual: recta sobre TODAS las mediciones de la vida
        hx = (hasta.horas_inicio_vida + hasta.horas_ciclo).values
        pend, ord0 = np.polyfit(hx, hasta.profundidad_medida_mm.values, 1)
        rul_recta = (G.UMBRAL_RETIRO_MM - ord0) / pend - h_ahora if pend < 0 else np.nan
        # (b) modelo: tasa prevista con las condiciones de la última ventana
        w = ventanas(hasta.tail(VENTANA).assign(ciclo=range(1, VENTANA + 1)))
        if w.empty:
            continue
        tasa = float(np.exp(modelo_gb.predict(w[list(VARIABLES)]))[0])
        rul_modelo = (d_ahora - G.UMBRAL_RETIRO_MM) / tasa * 100
        filas.append({"serial": serial, "real": real, "recta": rul_recta, "modelo": rul_modelo})
    return pd.DataFrame(filas).dropna()


def resumen_rul(r):
    out = {}
    for m in ("recta", "modelo"):
        e = r[m] - r.real
        out[m] = {"mae_h": round(float(e.abs().mean()), 0),
                  "dentro_200h_pct": round(float((e.abs() <= 200).mean() * 100), 1),
                  "optimista_pct": round(float((e > 200).mean() * 100), 1)}  # predice más vida de la real: riesgo
    out["n"] = len(r)
    return out


# ---------------------------------------------------------------- 3. supervivencia (daño)
def tabla_vidas(c, vidas):
    c = c.assign(roca=(c.terreno == "roca_suelta").astype(float),
                 sobrecarga=((c.carga_t / G.CARGA_NOMINAL_T - 1) * 100).clip(lower=0),
                 caliente=(c.temp_neumatico_c > 95).astype(float),
                 presion_baja=(-c.presion_desv_pct).clip(lower=0))
    g = c.groupby("serial").agg(frac_roca_suelta=("roca", "mean"), pendiente_rel=("pendiente_pct", "mean"),
                                sobrecarga_pct=("sobrecarga", "mean"), frac_temp_sobre_95=("caliente", "mean"),
                                presion_baja_pct=("presion_baja", "mean"), frenadas_por_h=("frenadas_por_h", "mean"))
    g["pendiente_rel"] -= 6
    t = vidas.set_index("serial").join(g)
    t["evento_dano"] = (t.fin == "dano").astype(int)
    return t


def main():
    c = pd.read_csv(DATOS / "ciclos.csv")
    vidas = pd.read_csv(DATOS / "vidas.csv")
    w = ventanas(c)
    gss = GroupShuffleSplit(n_splits=1, test_size=0.2, random_state=7)
    tr_i, te_i = next(gss.split(w, groups=w.caex))
    tr, te = w.iloc[tr_i], w.iloc[te_i]
    camiones_test = set(te.caex)
    print(f"ventanas: {len(w):,} (entrenamiento {len(tr):,} · prueba {len(te):,} de {len(camiones_test)} camiones no vistos)")

    # 2a. regresión con indicadores
    lin = LinearRegression().fit(matriz_indicadores(tr), np.log(tr.tasa_obs))
    rec = pd.DataFrame([{"variable": n, "unidad": u, "efecto_verdadero_pct": 100 * (np.exp(v) - 1),
                         "efecto_estimado_pct": 100 * (np.exp(b) - 1)}
                        for (k, (n, v, u)), b in zip(INDICADORES.items(), lin.coef_)])
    # el TKPH entra en logaritmo: su coeficiente es una elasticidad; se expresa como efecto de +10 % de TKPH
    rec.loc[rec.variable == "TKPH", ["efecto_verdadero_pct", "efecto_estimado_pct"]] = \
        [100 * (1.1 ** G.VERDAD_DESGASTE["tkph_rel"] - 1),
         100 * (1.1 ** lin.coef_[list(INDICADORES).index("log_tkph")] - 1)]

    # 2b. Gradient Boosting sobre variables en bruto + SHAP
    gb = HistGradientBoostingRegressor(max_iter=400, learning_rate=0.05, max_leaf_nodes=31, random_state=7)
    gb.fit(tr[list(VARIABLES)], np.log(tr.tasa_obs))
    pred = {"Promedio de flota": np.full(len(te), tr.tasa_obs.mean()),
            "Regresión multivariable": np.exp(lin.predict(matriz_indicadores(te))),
            "Gradient Boosting": np.exp(gb.predict(te[list(VARIABLES)]))}
    mae = {k: round(float(np.abs(p - te.tasa_real).mean()), 3) for k, p in pred.items()}
    piso = round(float(np.abs(te.tasa_obs - te.tasa_real).mean()), 3)
    muestra = te.sample(min(3000, len(te)), random_state=1)[list(VARIABLES)]
    sv = shap.TreeExplainer(gb).shap_values(muestra)
    imp = pd.Series(np.abs(sv).mean(0), index=[VARIABLES[k] for k in VARIABLES]).sort_values()

    # 3. supervivencia
    tv = tabla_vidas(c, vidas)
    cov = ["frac_roca_suelta", "pendiente_rel", "sobrecarga_pct", "frac_temp_sobre_95", "presion_baja_pct", "frenadas_por_h"]
    tv_tr, tv_te = tv[~tv.caex.isin(camiones_test)], tv[tv.caex.isin(camiones_test)]
    cph = CoxPHFitter(penalizer=0.01).fit(tv_tr[cov + ["horas_vida", "evento_dano"]], "horas_vida", "evento_dano")
    verdad_hr = {"frac_roca_suelta": np.exp(G.VERDAD_DANO["terreno_roca_suelta"]),
                 "pendiente_rel": np.exp(G.VERDAD_DANO["pendiente_pct"]),
                 "sobrecarga_pct": np.exp(G.VERDAD_DANO["sobrecarga_pct"]),
                 "frac_temp_sobre_95": np.exp(G.VERDAD_DANO["temp_sobre_95"]),
                 "presion_baja_pct": 1.0, "frenadas_por_h": 1.0}
    hr = pd.DataFrame({"hr_verdadero": verdad_hr, "hr_estimado": np.exp(cph.params_),
                       "ic95_inf": np.exp(cph.confidence_intervals_.iloc[:, 0]),
                       "ic95_sup": np.exp(cph.confidence_intervals_.iloc[:, 1])}).loc[cov]
    c_index = float(cph.score(tv_te[cov + ["horas_vida", "evento_dano"]], scoring_method="concordance_index"))

    # 4. horas remanentes
    c_te = c[c.caex.isin(camiones_test) & c.serial.isin(vidas.serial[vidas.fin == "desgaste"])]
    rul = {f"a_{p}_mm": resumen_rul(rul_en_punto(c_te, gb, p)) for p in (45, 30)}
    r30 = rul_en_punto(c_te, gb, 30)

    # ---------------------------------------------------------- gráficos
    fig, ax = plt.subplots(figsize=(8, 5.5))
    imp.plot.barh(ax=ax, color="#2a6f97")
    ax.set_xlabel("Importancia media |SHAP| sobre log(tasa de desgaste)")
    ax.set_title("Variables que explican el desgaste (SHAP)")
    fig.tight_layout(); fig.savefig(RES / "importancia_shap.png", dpi=130); plt.close(fig)

    fig, ax = plt.subplots(figsize=(8, 5.5))
    y = np.arange(len(rec))
    ax.barh(y + 0.2, rec.efecto_verdadero_pct, 0.4, label="Efecto verdadero (simulador)", color="#adb5bd")
    ax.barh(y - 0.2, rec.efecto_estimado_pct, 0.4, label="Efecto estimado (regresión)", color="#2a6f97")
    ax.set_yticks(y, rec.variable); ax.axvline(0, color="k", lw=0.8); ax.legend(loc="lower right")
    ax.set_xlabel("Cambio % en la tasa de desgaste por unidad (ver tabla)")
    ax.set_title("¿El modelo recupera los efectos conocidos?")
    fig.tight_layout(); fig.savefig(RES / "recuperacion_efectos.png", dpi=130); plt.close(fig)

    fig, ax = plt.subplots(figsize=(6.5, 6))
    lim = [0, max(r30.real.max(), r30.modelo.max(), r30.recta.clip(upper=3000).max()) * 1.05]
    ax.scatter(r30.real, r30.recta.clip(upper=lim[1]), s=14, alpha=0.6, label="Método actual (recta)", color="#adb5bd")
    ax.scatter(r30.real, r30.modelo, s=14, alpha=0.7, label="Modelo (Gradient Boosting)", color="#2a6f97")
    ax.plot(lim, lim, "k--", lw=0.8); ax.fill_between(lim, [l - 200 for l in lim], [l + 200 for l in lim], color="#2a6f97", alpha=0.08, label="±200 h")
    ax.set_xlim(lim); ax.set_ylim(lim); ax.legend()
    ax.set_xlabel("Horas remanentes reales"); ax.set_ylabel("Horas remanentes estimadas")
    ax.set_title("Horas remanentes al llegar a 30 mm (camiones no vistos)")
    fig.tight_layout(); fig.savefig(RES / "rul_30mm.png", dpi=130); plt.close(fig)

    metricas = {"ventanas": len(w), "camiones_prueba": len(camiones_test),
                "mae_tasa_mm_100h": mae, "piso_ruido_medicion": piso, "rul": rul,
                "c_index_dano": round(c_index, 3),
                "importancia_shap": {k: round(float(v), 4) for k, v in imp.sort_values(ascending=False).items()}}
    (RES / "metricas.json").write_text(json.dumps(metricas, ensure_ascii=False, indent=2), encoding="utf-8")
    escribir_reporte(metricas, rec, hr, vidas)
    # copia gráficos y métricas al prototipo (página "Modelos", src/index.html#/modelos)
    publico = RAIZ.parent / "src" / "assets" / "modelo"
    publico.mkdir(parents=True, exist_ok=True)
    for archivo in ("importancia_shap.png", "rul_30mm.png", "recuperacion_efectos.png", "metricas.json"):
        (publico / archivo).write_bytes((RES / archivo).read_bytes())
    print(json.dumps(metricas, ensure_ascii=False, indent=1))


def escribir_reporte(m, rec, hr, vidas):
    f = lambda x: f"{x:+.1f} %"
    filas_rec = "\n".join(f"| {r.variable} | {r.unidad} | {f(r.efecto_verdadero_pct)} | {f(r.efecto_estimado_pct)} |"
                          for r in rec.itertuples())
    filas_hr = "\n".join(f"| {k} | {r.hr_verdadero:.2f} | {r.hr_estimado:.2f} ({r.ic95_inf:.2f} – {r.ic95_sup:.2f}) |"
                         for k, r in hr.iterrows())
    filas_mae = "\n".join(f"| {k} | {v:.3f} |" for k, v in m["mae_tasa_mm_100h"].items())
    filas_rul = "\n".join(
        f"| {p.replace('a_', '').replace('_mm', ' mm')} | {r['n']} | {r['recta']['mae_h']:.0f} h · {r['recta']['dentro_200h_pct']} % · {r['recta']['optimista_pct']} % "
        f"| {r['modelo']['mae_h']:.0f} h · {r['modelo']['dentro_200h_pct']} % · {r['modelo']['optimista_pct']} % |"
        for p, r in m["rul"].items())
    top = list(m["importancia_shap"])[:5]
    texto = f"""# Reporte de la PoC: modelo de desgaste y vida útil remanente

> Generado por `modelo/entrenar.py` con **datos sintéticos** (`modelo/generar_datos.py`, semilla {G.SEMILLA}).
> Los efectos verdaderos son conocidos; el objetivo es comprobar que el método los recupera antes de usar datos reales.

**Datos:** {len(vidas):,} vidas de neumático en {G.CAMIONES} CAEX ({(vidas.fin == 'desgaste').mean():.0%} terminan por desgaste,
{(vidas.fin == 'dano').mean():.0%} por daño y {(vidas.fin == 'censurado').mean():.0%} siguen montadas al cierre) · {m['ventanas']:,} ventanas de ~200 h.
**Validación:** {m['camiones_prueba']} camiones completos reservados para prueba (el modelo nunca los vio).

## 1. Variables que más explican el desgaste (SHAP)
![Importancia SHAP](importancia_shap.png)

Las cinco primeras: {', '.join(top)}.

## 2. ¿Se recuperan los efectos conocidos? (regresión multivariable)
![Recuperación de efectos](recuperacion_efectos.png)

| Variable | Unidad | Efecto verdadero | Efecto estimado |
|---|---|---|---|
{filas_rec}

## 3. Precisión de la tasa de desgaste (camiones no vistos)
Error absoluto medio frente a la tasa real (mm/100 h). El piso por ruido de medición del pórtico es {m['piso_ruido_medicion']:.3f}.

| Modelo | MAE (mm/100 h) |
|---|---|
{filas_mae}

## 4. Horas remanentes (RUL) frente al método actual
Método actual = recta de profundidad vs horas sobre todas las mediciones del neumático (`backend/app/proyeccion.py`).
Cada celda: error medio · % de estimaciones dentro de ±200 h · % **optimistas** (predicen más de 200 h de vida extra, el error peligroso).
«Dentro de ±200 h» mide el error de la estimación; **no demuestra** que el modelo anticipe una falla con 200 h de antelación (META-01).

| Punto de evaluación | N | Método actual | Modelo |
|---|---|---|---|
{filas_rul}

![RUL a 30 mm](rul_30mm.png)

## 5. Riesgo de daño prematuro (supervivencia, Cox)
Razón de riesgo (HR) por unidad. HR = 1 significa sin efecto. Índice de concordancia en camiones no vistos: **{m['c_index_dano']:.2f}**.

| Covariable | HR verdadero | HR estimado (IC 95 %) |
|---|---|---|
{filas_hr}
"""
    (RES / "REPORTE.md").write_text(texto, encoding="utf-8")


if __name__ == "__main__":
    main()
