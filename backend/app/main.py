"""API base con datos de ejemplo en memoria. Reemplazar por PostgreSQL."""
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from .proyeccion import proyectar_horas, semaforo, tasa_desgaste_por_100h

app = FastAPI(title="Control de neumáticos CAEX")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

UMBRAL_MM = 20.0
MODELO_VERSION = "v1.3"


def _hist(horas_rest: float, tasa=1.1, n=8, paso_h=100):
    """Historial sintético: profundidad por pasada que llega a la proyección dada con umbral 20.0 mm."""
    fin = UMBRAL_MM + horas_rest * tasa / 100
    return [(i * paso_h, round(fin + (n - 1 - i) * tasa, 2)) for i in range(n)]


NEUMATICOS = {
    s: {"serial": s, "caex": c, "posicion": p, "marca": m, "dano": d, "mediciones": _hist(h, tasa=t)}
    for s, c, p, m, h, t, d in [
        ("5980R63-2426-1348", "CAEX-102", 3, "Bridgestone", 34, 1.17, "corte profundo en flanco"),
        ("5980R63-2328-1590", "CAEX-106", 2, "Bridgestone", 95, 1.79, "desgaste irregular"),
        ("5980R63-2345-1534", "CAEX-105", 5, "Michelin", 106, 1.14, None),
        ("5980R63-2618-1611", "CAEX-106", 5, "Bridgestone", 143, 1.61, None),
        ("5980R63-2531-1596", "CAEX-106", 4, "Bridgestone", 150, 1.94, "roca incrustada en la banda"),
        ("5980R63-2312-1561", "CAEX-105", 2, "Michelin", 168, 2.44, None),
        ("5980R63-2218-1478", "CAEX-103", 5, "BKT", 392, 1.10, None),
        ("5980R63-2100-1301", "CAEX-101", 1, "Bridgestone", 1687, 1.10, None),
        ("5980R63-2150-1355", "CAEX-104", 6, "Michelin", 4020, 1.10, None),
    ]
}

VENTANAS = [
    {"id": 1, "dia": "29-09-2026", "turno": "turno B, 20:00 a 00:00", "libres": 2, "horas_hasta": 36},
    {"id": 2, "dia": "30-09-2026", "turno": "turno A, 08:00 a 12:00", "libres": 1, "horas_hasta": 56},
    {"id": 3, "dia": "01-10-2026", "turno": "turno B, 20:00 a 00:00", "libres": 3, "horas_hasta": 84},
]
ORDENES: list[dict] = []


def _resumen(n: dict) -> dict:
    h = proyectar_horas(n["mediciones"], UMBRAL_MM)
    return {**{k: n[k] for k in ("serial", "caex", "posicion", "marca")},
            "horas_restantes": round(h) if h is not None else None,
            "semaforo": semaforo(h) if h is not None else "verde"}


@app.get("/turnos/{fecha}/neumaticos")
def tablero(fecha: str):
    filas = [_resumen(n) for n in NEUMATICOS.values()]
    return sorted(filas, key=lambda f: f["horas_restantes"] if f["horas_restantes"] is not None else 1e9)


@app.get("/neumaticos/{serial}")
def ficha(serial: str):
    n = NEUMATICOS.get(serial)
    if not n:
        raise HTTPException(404, "Neumático no encontrado")
    return {**_resumen(n), "ultimo_dano": n["dano"], "umbral_mm": UMBRAL_MM,
            "tasa_mm_por_100h": tasa_desgaste_por_100h(n["mediciones"]),
            "historial": [{"horas": h, "profundidad_mm": p} for h, p in n["mediciones"]]}


@app.get("/neumaticos/{serial}/ventanas")
def ventanas(serial: str):
    n = NEUMATICOS.get(serial)
    if not n:
        raise HTTPException(404, "Neumático no encontrado")
    h = proyectar_horas(n["mediciones"], UMBRAL_MM) or 0
    return [{**v, "dentro_del_margen": v["horas_hasta"] < h} for v in VENTANAS]


class NuevaOrden(BaseModel):
    serial: str
    ventana_id: int


@app.post("/ordenes", status_code=201)
def crear_orden(body: NuevaOrden):
    n = NEUMATICOS.get(body.serial)
    v = next((x for x in VENTANAS if x["id"] == body.ventana_id), None)
    if not n or not v:
        raise HTTPException(404, "Neumático o ventana no encontrados")
    if v["libres"] < 1:
        raise HTTPException(409, "La ventana no tiene cupos libres")
    v["libres"] -= 1
    orden = {"codigo": f"OT-2026-{918 + len(ORDENES):04d}", "serial": n["serial"], "caex": n["caex"],
             "posicion": n["posicion"], "ventana": f'{v["dia"]}, turno {v["turno"]}',
             "modelo_version": MODELO_VERSION, "ventana_id": v["id"], "estado": "programada", "historial": []}
    ORDENES.append(orden)  # TODO: escribir en ERP y notificar al taller
    return orden


class CambioOrden(BaseModel):
    ventana_id: Optional[int] = None
    nota: Optional[str] = None
    motivo: str


class AnulacionOrden(BaseModel):
    motivo: str


def _orden_programada(codigo: str) -> dict:
    orden = next((o for o in ORDENES if o["codigo"] == codigo), None)
    if not orden:
        raise HTTPException(404, "Orden no encontrada")
    if orden["estado"] != "programada":
        raise HTTPException(409, f'La orden está {orden["estado"]} y no se puede modificar')
    return orden


def _liberar(orden: dict):
    v = next((x for x in VENTANAS if x["id"] == orden["ventana_id"]), None)
    if v:
        v["libres"] += 1


@app.patch("/ordenes/{codigo}")
def modificar_orden(codigo: str, body: CambioOrden):
    orden = _orden_programada(codigo)
    if not body.motivo.strip():
        raise HTTPException(422, "El motivo del cambio es obligatorio")
    cambios = []
    if body.ventana_id is not None and body.ventana_id != orden["ventana_id"]:
        nueva = next((x for x in VENTANAS if x["id"] == body.ventana_id), None)
        if not nueva:
            raise HTTPException(404, "Ventana no encontrada")
        if nueva["libres"] < 1:
            raise HTTPException(409, "La ventana no tiene cupos libres")
        _liberar(orden)
        nueva["libres"] -= 1
        orden["ventana_id"] = nueva["id"]
        orden["ventana"] = f'{nueva["dia"]}, turno {nueva["turno"]}'
        cambios.append("ventana")
    if body.nota is not None and body.nota != orden.get("nota"):
        orden["nota"] = body.nota
        cambios.append("nota")
    if not cambios:
        raise HTTPException(422, "No hay cambios que guardar")
    orden["historial"].append({"accion": "modificada", "cambios": cambios, "motivo": body.motivo})
    return orden  # TODO: notificar al taller y actualizar el ERP


@app.post("/ordenes/{codigo}/anular")
def anular_orden(codigo: str, body: AnulacionOrden):
    orden = _orden_programada(codigo)
    if not body.motivo.strip():
        raise HTTPException(422, "El motivo de anulación es obligatorio")
    _liberar(orden)
    orden["estado"] = "anulada"  # la orden no se borra: es evidencia
    orden["historial"].append({"accion": "anulada", "motivo": body.motivo})
    return orden
