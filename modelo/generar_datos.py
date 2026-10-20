"""Genera datos sintéticos de operación y condición de neumáticos OTR para la PoC.

Los efectos de cada variable sobre el desgaste y sobre el riesgo de daño son CONOCIDOS
(constantes VERDAD_* más abajo). Así se puede comprobar si el modelo los recupera
antes de contar con datos reales de la faena.

Unidad de observación: un ciclo de operación de ~50 h entre dos pasadas por el pórtico.

Uso (desde la raíz del repositorio):
    modelo/.venv/Scripts/python modelo/generar_datos.py
Salida: modelo/datos/ciclos.csv y modelo/datos/vidas.csv
"""
from pathlib import Path

import numpy as np
import pandas as pd

SEMILLA = 2026
CAMIONES = 67
POSICIONES = 6
HORAS_OBSERVACION = 12_000        # unos dos años de operación por camión
HORAS_CICLO_MEDIA = 50
PROFUNDIDAD_NUEVO_MM = 95.0
UMBRAL_RETIRO_MM = 20.0           # el mismo umbral del prototipo
RUIDO_PORTICO_MM = 0.25           # desviación estándar de la medición del pórtico

PESO_VACIO_T = 160.0              # Cat 793F aproximado
CARGA_NOMINAL_T = 227.0
TKPH_REFERENCIA = 900.0

# ---------------------------------------------------------------------------
# VERDAD: efectos reales usados para simular. El modelo NO los conoce.
# Tasa de desgaste (mm/100 h) = TASA_BASE * exp(suma de efectos) * ruido
# ---------------------------------------------------------------------------
TASA_BASE = 1.10
VERDAD_DESGASTE = {
    "presion_baja_pct": 0.015,      # +1,5 % de desgaste por cada 1 % bajo la presión nominal
    "presion_alta_pct": 0.005,      # +0,5 % por cada 1 % sobre la presión nominal
    "tkph_rel": 0.60,               # elasticidad respecto de TKPH / TKPH_REFERENCIA
    "terreno_roca_suelta": np.log(1.30),
    "terreno_barro": np.log(1.10),
    "pendiente_pct": 0.030,         # +3 % por cada punto de pendiente media
    "posicion_delantera": np.log(1.15),  # neumáticos direccionales
    "frenadas_por_h": 0.020,        # +2 % por frenada fuerte adicional por hora
    "temp_ambiente_c": 0.005,       # +0,5 % por °C sobre 20 °C
}
# Efectos no lineales (los que un modelo lineal no captura bien)
VERDAD_INTERACCION_PRESION_TKPH = 0.012   # la presión baja daña más cuando el TKPH es alto
VERDAD_PENDIENTE_UMBRAL = 6.0             # sobre 6 % de pendiente el efecto se duplica

# Riesgo de daño por ciclo (corte, impacto, separación): modelo de riesgos proporcionales
RIESGO_BASE_CICLO = 0.0020
VERDAD_DANO = {
    "terreno_roca_suelta": np.log(3.0),
    "pendiente_pct": 0.08,
    "sobrecarga_pct": 0.05,
    "temp_sobre_95": np.log(2.0),
}

TERRENOS = ["compactado", "roca_suelta", "barro"]


def perfil_ruta(rng):
    """Una fase de la mina: mezcla de terreno, pendiente y velocidad típica."""
    terreno = rng.choice(TERRENOS, p=[0.55, 0.30, 0.15])
    return {
        "terreno": terreno,
        "pendiente": float(np.clip(rng.normal(6.0, 2.5), 0.5, 12.0)),
        "velocidad": float(np.clip(rng.normal(21.0, 3.5), 12.0, 32.0)),
        "frenadas": float(np.clip(rng.normal(10.0, 3.0), 3.0, 22.0)),
    }


def simular(rng):
    ciclos, vidas = [], []
    id_vida = 0
    for c in range(CAMIONES):
        caex = f"CAEX-{101 + c}"
        sesgo_presion = rng.normal(-2.0, 4.0)          # algunos camiones andan bajos de presión
        sesgo_carga = rng.normal(0.0, 4.0)             # % de sobrecarga habitual del camión
        rutas = []                                     # el camión cambia de fase cada ~1.500 h
        h = 0.0
        while h < HORAS_OBSERVACION:
            dur = rng.uniform(800, 2200)
            rutas.append((h, h + dur, perfil_ruta(rng)))
            h += dur

        def ruta_en(t):
            return next(r for (a, b, r) in rutas if a <= t < b)

        for pos in range(1, POSICIONES + 1):
            delantera = pos <= 2
            t = 0.0
            while t < HORAS_OBSERVACION:
                id_vida += 1
                serial = f"SIM-{id_vida:05d}"
                inicio = t
                prof = PROFUNDIDAD_NUEVO_MM
                prof_medida_ant = prof + rng.normal(0, RUIDO_PORTICO_MM)
                presion_neumatico = sesgo_presion + rng.normal(0, 2.0)
                fin_tipo = "censurado"
                n = 0
                while True:
                    n += 1
                    horas = float(np.clip(rng.normal(HORAS_CICLO_MEDIA, 8), 30, 70))
                    r = ruta_en(t)
                    amb = 20 + 8 * np.sin(2 * np.pi * t / 6000) + rng.normal(0, 3)
                    presion_desv = presion_neumatico + rng.normal(0, 1.5)
                    sobrecarga = sesgo_carga + rng.normal(0, 3)
                    carga = CARGA_NOMINAL_T * (1 + sobrecarga / 100)
                    vel = r["velocidad"] * rng.uniform(0.9, 1.1)
                    distancia = vel * horas * 0.85
                    frenadas = r["frenadas"] * rng.uniform(0.85, 1.15)
                    pend = r["pendiente"] + rng.normal(0, 0.4)
                    # TKPH: carga media por neumático (t) x velocidad media (km/h)
                    peso_medio = PESO_VACIO_T + carga / 2
                    q_neumatico = peso_medio * (0.33 / 2 if delantera else 0.67 / 4)
                    tkph = q_neumatico * vel
                    # la temperatura es CONSECUENCIA de la carga, la presión y el ambiente (no causa)
                    temp = 30 + 0.045 * tkph + 0.6 * amb + 0.8 * max(0, -presion_desv) + rng.normal(0, 3)

                    baja, alta = max(0, -presion_desv), max(0, presion_desv)
                    log_tasa = (np.log(TASA_BASE)
                                + VERDAD_DESGASTE["presion_baja_pct"] * baja
                                + VERDAD_DESGASTE["presion_alta_pct"] * alta
                                + VERDAD_DESGASTE["tkph_rel"] * np.log(tkph / TKPH_REFERENCIA)
                                + VERDAD_DESGASTE["terreno_roca_suelta"] * (r["terreno"] == "roca_suelta")
                                + VERDAD_DESGASTE["terreno_barro"] * (r["terreno"] == "barro")
                                + VERDAD_DESGASTE["pendiente_pct"] * pend
                                + VERDAD_DESGASTE["pendiente_pct"] * max(0, pend - VERDAD_PENDIENTE_UMBRAL)
                                + VERDAD_DESGASTE["posicion_delantera"] * delantera
                                + VERDAD_DESGASTE["frenadas_por_h"] * (frenadas - 10)
                                + VERDAD_DESGASTE["temp_ambiente_c"] * (amb - 20)
                                + VERDAD_INTERACCION_PRESION_TKPH * baja * max(0, tkph / TKPH_REFERENCIA - 1) * 10)
                    tasa_real = np.exp(log_tasa) * rng.lognormal(0, 0.06)
                    prof -= tasa_real * horas / 100
                    prof_medida = prof + rng.normal(0, RUIDO_PORTICO_MM)

                    log_riesgo = (np.log(RIESGO_BASE_CICLO)
                                  + VERDAD_DANO["terreno_roca_suelta"] * (r["terreno"] == "roca_suelta")
                                  + VERDAD_DANO["pendiente_pct"] * (pend - 6)
                                  + VERDAD_DANO["sobrecarga_pct"] * max(0, sobrecarga)
                                  + VERDAD_DANO["temp_sobre_95"] * (temp > 95))
                    dano = rng.random() < 1 - np.exp(-np.exp(log_riesgo))

                    ciclos.append({
                        "serial": serial, "caex": caex, "posicion": pos, "ciclo": n,
                        "horas_inicio_vida": round(t - inicio, 1), "horas_ciclo": round(horas, 1),
                        "presion_desv_pct": round(presion_desv, 2), "temp_neumatico_c": round(temp, 1),
                        "carga_t": round(carga, 1), "velocidad_kmh": round(vel, 2),
                        "distancia_km": round(distancia, 1), "terreno": r["terreno"],
                        "pendiente_pct": round(pend, 2), "frenadas_por_h": round(frenadas, 2),
                        "temp_ambiente_c": round(amb, 1), "tkph": round(tkph, 1),
                        "profundidad_medida_mm": round(prof_medida, 2),
                        "profundidad_anterior_mm": round(prof_medida_ant, 2),
                        "tasa_real_mm_100h": round(tasa_real, 4),          # solo para validar; no es un insumo
                        "profundidad_real_mm": round(prof, 3),             # solo para validar
                    })
                    prof_medida_ant = prof_medida
                    t += horas
                    if dano:
                        fin_tipo = "dano"
                        break
                    if prof <= UMBRAL_RETIRO_MM:
                        fin_tipo = "desgaste"
                        break
                    if t >= HORAS_OBSERVACION:
                        break
                vidas.append({"serial": serial, "caex": caex, "posicion": pos,
                              "horas_vida": round(t - inicio, 1), "fin": fin_tipo, "ciclos": n})
    return pd.DataFrame(ciclos), pd.DataFrame(vidas)


if __name__ == "__main__":
    salida = Path(__file__).resolve().parent / "datos"
    salida.mkdir(exist_ok=True)
    ciclos, vidas = simular(np.random.default_rng(SEMILLA))
    ciclos.to_csv(salida / "ciclos.csv", index=False)
    vidas.to_csv(salida / "vidas.csv", index=False)
    print(f"{len(ciclos):,} ciclos · {len(vidas):,} vidas de neumático · "
          f"fin por desgaste {(vidas.fin == 'desgaste').mean():.0%}, por daño {(vidas.fin == 'dano').mean():.0%}, "
          f"censuradas {(vidas.fin == 'censurado').mean():.0%}")
