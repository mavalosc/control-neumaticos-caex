#!/usr/bin/env bash
# Genera docs/wireframes/W1..W5.png desde el prototipo real con Chrome headless.
# Uso (desde la raíz del repo, en Git Bash): bash scripts/wireframes/generar.sh
set -e
CHROME="${CHROME:-/c/Program Files/Google/Chrome/Application/chrome.exe}"
PUERTO=8766
python -m http.server $PUERTO >/dev/null 2>&1 &
SERVIDOR=$!
trap 'kill $SERVIDOR' EXIT
sleep 1
SALIDA="$(cygpath -w "$PWD/docs/wireframes" 2>/dev/null || echo "$PWD/docs/wireframes")"
for w in 1 2 3 4 5; do
  "$CHROME" --headless=new --disable-gpu --hide-scrollbars --user-data-dir="$(mktemp -d)" \
    --window-size=1740,1000 --virtual-time-budget=6000 \
    --screenshot="$SALIDA/W$w.png" "http://localhost:$PUERTO/scripts/wireframes/anotar.html?w=$w" 2>/dev/null
  echo "docs/wireframes/W$w.png"
done
