"""Generador de datos de terreno SIMULADOS (PROP-06).

Simula, para cada neumático montado en la flota de Supabase, un ciclo de operación por día:
presión (TPMS), temperatura, carga, velocidad, distancia, terreno, pendiente, frenadas, TKPH
y la profundidad que mediría el pórtico. Guarda las filas en `ciclos_operacion` con
origen = 'simulado'. No escribe en `mediciones` (decisión del equipo, 25-10-2026).

- Primera ejecución: genera un historial de DIAS_HISTORIAL días por neumático.
- Ejecuciones siguientes: agrega los días que falten hasta hoy (idempotente).
- Los efectos de cada variable son los del simulador de la prueba de concepto
  (modelo/generar_datos.py, constantes VERDAD_*): son SUPUESTOS, no mediciones.

Uso:
    python modelo/terreno/generar_terreno.py            # escribe en Supabase (requiere service_role)
    python modelo/terreno/generar_terreno.py --prueba   # solo lee y guarda modelo/datos/terreno_ciclos.csv
"""
import argparse
import datetime as dt
import hashlib
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import generar_datos as G  # noqa: E402  efectos y constantes del simulador
from terreno.supabase_api import Supabase, RAIZ  # noqa: E402

DIAS_HISTORIAL = 150                 # ≈ 3.000 h de operación por neumático en la primera carga
PRESION_NOMINAL_PSI = 102            # el mismo supuesto del simulador del pórtico en la app
MODELOS = {"Cat 793F": (160, 227), "Komatsu 930E-4": (200, 290), "Cat 797F": (260, 363)}  # (vacío, carga nominal) t
TERRENOS = ["compactado", "roca_suelta", "barro"]


def semilla(*partes):
    """Semilla estable a partir de texto: el mismo neumático y día generan siempre lo mismo."""
    return int(hashlib.sha256("|".join(map(str, partes)).encode()).hexdigest()[:12], 16)


def perfil_camion(caex, dia_abs):
    """Fase de la mina del camión: cambia cada 60 a 110 días (terreno, pendiente, velocidad, frenadas)."""
    duracion = 60 + semilla(caex, "fase") % 51
    fase = dia_abs // duracion
    r = np.random.default_rng(semilla(caex, "fase", fase))
    return {
        "terreno": r.choice(TERRENOS, p=[0.55, 0.30, 0.15]),
        "pendiente": float(np.clip(r.normal(6.0, 2.5), 0.5, 12.0)),
        "velocidad": float(np.clip(r.normal(21.0, 3.5), 12.0, 32.0)),
        "frenadas": float(np.clip(r.normal(10.0, 3.0), 3.0, 22.0)),
    }


def simular_ciclo(n, dia, estado):
    """Un día de operación de un neumático. `estado` trae vida, ciclo, horas y profundidad real."""
    dia_abs = (dia - dt.date(2026, 1, 1)).days
    r = np.random.default_rng(semilla(n["serial"], estado["vida"], estado["ciclo"]))
    p = perfil_camion(n["caex"], dia_abs)
    vacio, nominal = MODELOS.get(n["modelo"], MODELOS["Cat 793F"])
    sesgo_presion = (semilla(n["serial"], "presion") % 900) / 100 - 6.5      # -6,5 % a +2,5 % según el neumático
    sesgo_carga = (semilla(n["caex"], "carga") % 1000) / 100 - 4.0           # -4 % a +6 % según el camión
    delantera = n["posicion"] <= 2

    horas = float(np.clip(r.normal(19, 2), 14, 23))
    amb = 15 + 8 * np.sin(2 * np.pi * (dia_abs - 30) / 365) + r.normal(0, 3)
    presion = sesgo_presion + r.normal(0, 1.5)
    sobrecarga = sesgo_carga + r.normal(0, 3)
    carga = nominal * (1 + sobrecarga / 100)
    vel = p["velocidad"] * r.uniform(0.9, 1.1)
    frenadas = p["frenadas"] * r.uniform(0.85, 1.15)
    pend = p["pendiente"] + r.normal(0, 0.4)
    q = (vacio + carga / 2) * (0.33 / 2 if delantera else 0.67 / 4)
    tkph = q * vel
    temp = 30 + 0.045 * tkph + 0.6 * amb + 0.8 * max(0, -presion) + r.normal(0, 3)

    V = G.VERDAD_DESGASTE
    baja, alta = max(0, -presion), max(0, presion)
    log_tasa = (np.log(G.TASA_BASE) + V["presion_baja_pct"] * baja + V["presion_alta_pct"] * alta
                + V["tkph_rel"] * np.log(tkph / G.TKPH_REFERENCIA)
                + V["terreno_roca_suelta"] * (p["terreno"] == "roca_suelta") + V["terreno_barro"] * (p["terreno"] == "barro")
                + V["pendiente_pct"] * pend + V["pendiente_pct"] * max(0, pend - G.VERDAD_PENDIENTE_UMBRAL)
                + V["posicion_delantera"] * delantera + V["frenadas_por_h"] * (frenadas - 10)
                + V["temp_ambiente_c"] * (amb - 20)
                + G.VERDAD_INTERACCION_PRESION_TKPH * baja * max(0, tkph / G.TKPH_REFERENCIA - 1) * 10)
    tasa = float(np.exp(log_tasa) * r.lognormal(0, 0.06))
    prof = estado["profundidad"] - tasa * horas / 100

    fila = {
        "neumatico_id": n["id"], "serial": n["serial"], "caex_codigo": n["caex"], "posicion": n["posicion"],
        "vida": estado["vida"], "ciclo": estado["ciclo"], "fecha": dia.isoformat(),
        "horas_ciclo": round(horas, 1), "horas_vida": round(estado["horas"], 1),
        "presion_desv_pct": round(presion, 2), "presion_psi": round(PRESION_NOMINAL_PSI * (1 + presion / 100), 1),
        "temp_neumatico_c": round(temp, 1), "temp_ambiente_c": round(amb, 1), "carga_t": round(carga, 1),
        "velocidad_kmh": round(vel, 2), "distancia_km": round(vel * horas * 0.85, 1), "terreno": str(p["terreno"]),
        "pendiente_pct": round(pend, 2), "frenadas_por_h": round(frenadas, 2), "tkph": round(tkph, 1),
        "profundidad_mm": round(prof + r.normal(0, G.RUIDO_PORTICO_MM), 2),
        "profundidad_real_simulada": round(prof, 3), "tasa_real_simulada": round(tasa, 4), "origen": "simulado",
    }
    # siguiente estado: al llegar al umbral, el simulador modela el recambio por un neumático nuevo
    if prof <= G.UMBRAL_RETIRO_MM:
        return fila, {"vida": estado["vida"] + 1, "ciclo": 1, "horas": 0.0, "profundidad": G.PROFUNDIDAD_NUEVO_MM}
    return fila, {"vida": estado["vida"], "ciclo": estado["ciclo"] + 1, "horas": estado["horas"] + horas, "profundidad": prof}


def estado_inicial(n, dias):
    """Para el historial: parte con la profundidad medida hoy más el desgaste esperado del período."""
    prof = float(n["profundidad"] or 60) + 1.9 * 19 * dias / 100
    return {"vida": 1, "ciclo": 1, "horas": 0.0, "profundidad": min(prof, G.PROFUNDIDAD_NUEVO_MM)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--prueba", action="store_true", help="no escribe en Supabase; guarda un CSV local")
    ap.add_argument("--hasta", default=None, help="fecha final AAAA-MM-DD (por defecto: hoy en Chile)")
    args = ap.parse_args()
    sb = Supabase()
    prueba = args.prueba or sb.modo_prueba
    hoy = dt.date.fromisoformat(args.hasta) if args.hasta else (dt.datetime.utcnow() - dt.timedelta(hours=3)).date()

    flota = sb.leer("vista_tablero_turno", "neumatico_id,neumatico_serial,caex_codigo,caex_modelo,posicion,profundidad_mm")
    neumaticos = [{"id": f["neumatico_id"], "serial": f["neumatico_serial"], "caex": f["caex_codigo"],
                   "modelo": f["caex_modelo"], "posicion": f["posicion"], "profundidad": f["profundidad_mm"]} for f in flota]
    ultimos = {} if prueba else {u["neumatico_id"]: u for u in sb.leer(
        "vista_ultimo_ciclo", "neumatico_id,vida,ciclo,fecha,horas_vida,horas_ciclo,profundidad_real_simulada")}

    filas = []
    for n in neumaticos:
        u = ultimos.get(n["id"])
        if u:   # continuar desde el último ciclo guardado
            desde = dt.date.fromisoformat(u["fecha"]) + dt.timedelta(days=1)
            estado = {"vida": u["vida"], "ciclo": u["ciclo"] + 1, "horas": float(u["horas_vida"]) + float(u["horas_ciclo"]),
                      "profundidad": float(u["profundidad_real_simulada"])}
            if estado["profundidad"] <= G.UMBRAL_RETIRO_MM:
                estado = {"vida": u["vida"] + 1, "ciclo": 1, "horas": 0.0, "profundidad": G.PROFUNDIDAD_NUEVO_MM}
        else:   # primera carga: historial completo
            desde = hoy - dt.timedelta(days=DIAS_HISTORIAL - 1)
            estado = estado_inicial(n, DIAS_HISTORIAL)
        dia = desde
        while dia <= hoy:
            fila, estado = simular_ciclo(n, dia, estado)
            filas.append(fila)
            dia += dt.timedelta(days=1)

    print(f"{len(neumaticos)} neumáticos · {len(filas):,} ciclos nuevos hasta {hoy}")
    if prueba:
        import csv
        destino = RAIZ / "modelo" / "datos" / "terreno_ciclos.csv"
        destino.parent.mkdir(exist_ok=True)
        if filas:
            with open(destino, "w", newline="", encoding="utf-8") as f:
                w = csv.DictWriter(f, fieldnames=list(filas[0]))
                w.writeheader(); w.writerows(filas)
        print(f"MODO PRUEBA: no se escribió en Supabase; ciclos guardados en {destino.relative_to(RAIZ)}")
    elif filas:
        sb.insertar("ciclos_operacion", filas, conflicto="neumatico_id,vida,ciclo")
        print("ciclos guardados en Supabase (ciclos_operacion, origen = 'simulado')")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
