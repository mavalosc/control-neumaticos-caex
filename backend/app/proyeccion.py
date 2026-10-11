"""Proyección de horas remanentes y semáforo."""
from typing import Optional

UMBRAL_ROJO_H = 200
UMBRAL_AMARILLO_H = 500


def proyectar_horas(mediciones: list[tuple[float, float]], umbral_mm: float) -> Optional[float]:
    """mediciones: [(horas_operacion, profundidad_mm), ...]. Devuelve horas remanentes o None."""
    n = len(mediciones)
    if n < 2:
        return None
    mx = sum(h for h, _ in mediciones) / n
    my = sum(p for _, p in mediciones) / n
    den = sum((h - mx) ** 2 for h, _ in mediciones)
    if den == 0:
        return None
    pendiente = sum((h - mx) * (p - my) for h, p in mediciones) / den
    if pendiente >= 0:
        return None  # sin desgaste medible
    intercepto = my - pendiente * mx
    horas_umbral = (umbral_mm - intercepto) / pendiente
    return max(0.0, horas_umbral - mediciones[-1][0])


def tasa_desgaste_por_100h(mediciones: list[tuple[float, float]]) -> Optional[float]:
    if len(mediciones) < 2:
        return None
    (h0, p0), (h1, p1) = mediciones[0], mediciones[-1]
    return round((p0 - p1) / (h1 - h0) * 100, 2) if h1 != h0 else None


def semaforo(horas_restantes: float) -> str:
    if horas_restantes < UMBRAL_ROJO_H:
        return "rojo"
    if horas_restantes < UMBRAL_AMARILLO_H:
        return "amarillo"
    return "verde"
