"""Acceso mínimo a la API REST de Supabase (PostgREST) con la biblioteca estándar.

- Escritura: requiere la variable de entorno SUPABASE_SERVICE_ROLE_KEY (solo en los Secrets de GitHub
  o en el .env local, nunca en el código ni en la app).
- Sin esa variable se trabaja en MODO PRUEBA: se lee con la clave pública (anon) de src/config.js
  y no se escribe nada en la base.
"""
import json
import os
import re
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]


def _leer_env_local():
    """Carga SUPABASE_* desde el .env local si existe (para ejecutar en el computador del equipo)."""
    env = RAIZ / ".env"
    if env.exists():
        for linea in env.read_text(encoding="utf-8").splitlines():
            if "=" in linea and not linea.lstrip().startswith("#"):
                k, v = linea.split("=", 1)
                if k.strip() in ("SUPABASE_URL", "SUPABASE_SERVICE_ROLE_KEY") and k.strip() not in os.environ:
                    os.environ[k.strip()] = v.strip()


def _config_publica():
    texto = (RAIZ / "src" / "config.js").read_text(encoding="utf-8")
    url = re.search(r'SUPABASE_URL:\s*"([^"]+)"', texto).group(1)
    anon = re.search(r'SUPABASE_ANON_KEY:\s*"([^"]+)"', texto).group(1)
    return url, anon


class Supabase:
    def __init__(self):
        _leer_env_local()
        url_publica, anon = _config_publica()
        self.url = os.environ.get("SUPABASE_URL") or url_publica
        self.clave = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "").strip()
        self.modo_prueba = not self.clave
        if self.modo_prueba:
            self.clave = anon

    def _pedir(self, metodo, ruta, cuerpo=None, cabeceras=None):
        req = urllib.request.Request(
            f"{self.url}/rest/v1/{ruta}", method=metodo,
            data=json.dumps(cuerpo).encode("utf-8") if cuerpo is not None else None,
            headers={"apikey": self.clave, "Authorization": f"Bearer {self.clave}",
                     "Content-Type": "application/json", **(cabeceras or {})})
        try:
            with urllib.request.urlopen(req, timeout=120) as r:
                datos = r.read()
                return json.loads(datos) if datos else None
        except urllib.error.HTTPError as e:
            raise RuntimeError(f"{metodo} {ruta}: {e.code} {e.read().decode()[:300]}") from None

    def leer(self, tabla, columnas="*", filtros="", orden=None, bloque=1000):
        """Lee todas las filas, por bloques. Devuelve [] si la tabla aún no existe."""
        filas, desde = [], 0
        while True:
            q = f"{tabla}?select={urllib.parse.quote(columnas, safe='*,()')}{filtros}"
            if orden:
                q += f"&order={orden}"
            q += f"&offset={desde}&limit={bloque}"
            try:
                parte = self._pedir("GET", q)
            except RuntimeError as e:
                if "404" in str(e) or "42P01" in str(e) or "PGRST205" in str(e):
                    return []
                raise
            filas.extend(parte)
            if len(parte) < bloque:
                return filas
            desde += bloque

    def insertar(self, tabla, filas, conflicto=None, bloque=1000):
        """Inserta por bloques. Con `conflicto`, ignora filas repetidas (idempotente)."""
        if self.modo_prueba:
            raise RuntimeError("Modo prueba: falta SUPABASE_SERVICE_ROLE_KEY para escribir en la base.")
        cab = {"Prefer": "return=minimal" + (",resolution=ignore-duplicates" if conflicto else "")}
        ruta = tabla + (f"?on_conflict={conflicto}" if conflicto else "")
        for i in range(0, len(filas), bloque):
            self._pedir("POST", ruta, filas[i:i + bloque], cab)
