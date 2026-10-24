#!/usr/bin/env bash
# Regenera las capturas del manual y el PDF desde el prototipo real.
# Uso (desde la raíz del repositorio, en Git Bash): bash scripts/manual/generar.sh
# Requiere Python 3 y Google Chrome. Las capturas usan los datos actuales de Supabase.
set -e
CHROME="${CHROME:-/c/Program Files/Google/Chrome/Application/chrome.exe}"
PUERTO=8769
SALIDA_UNIX="$PWD/src/assets/manual"
mkdir -p "$SALIDA_UNIX"
SALIDA="$(cygpath -w "$SALIDA_UNIX" 2>/dev/null || echo "$SALIDA_UNIX")"
PERFIL="$(mktemp -d)"
python -m http.server $PUERTO >/dev/null 2>&1 &
SERVIDOR=$!
trap 'kill $SERVIDOR' EXIT
sleep 1

captura() {  # archivo  ruta  [código previo]
  local url="http://localhost:$PUERTO/scripts/manual/captura.html?r=$(MSYS_NO_PATHCONV=1 python -c 'import sys,urllib.parse;print(urllib.parse.quote(sys.argv[1]))' "$2")"
  [ -n "$3" ] && url="$url&prep=$(MSYS_NO_PATHCONV=1 python -c 'import sys,urllib.parse;print(urllib.parse.quote(sys.argv[1]))' "$3")"
  "$CHROME" --headless=new --disable-gpu --hide-scrollbars --user-data-dir="$PERFIL/$1" \
    --window-size=1400,900 --virtual-time-budget=9000 --screenshot="$SALIDA/$1" "$url" 2>/dev/null
  echo "src/assets/manual/$1"
}

captura 01-tablero.png    "/"
captura 02-camiones.png   "/c"
captura 03-ficha.png      "/n/5980R63-2426-1348"
captura 04-agendar.png    "/a/5980R63-2426-1348" "selectedWindowId = state.windows.find(w => w.libres > 0)?.id; renderSchedule('5980R63-2426-1348')"
captura 05-ordenes.png    "/o"
captura 06-modificar.png  "/e/ot-0068"
captura 07-simulador.png  "/sim"
captura 08-datos.png      "/datos"
captura 09-modelos.png    "/modelos"

"$CHROME" --headless=new --disable-gpu --user-data-dir="$PERFIL/pdf" --virtual-time-budget=10000 \
  --no-pdf-header-footer --print-to-pdf="$SALIDA/manual-control-neumaticos-caex.pdf" \
  "http://localhost:$PUERTO/scripts/manual/imprimir.html" 2>/dev/null
echo "src/assets/manual/manual-control-neumaticos-caex.pdf"
