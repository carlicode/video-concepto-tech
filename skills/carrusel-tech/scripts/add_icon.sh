#!/usr/bin/env bash
# Descarga un icono Lucide (licencia ISC) que no esté en assets/icons. Uso: add_icon.sh nombre-icono
# Es un SVG de ~1 KB desde jsDelivr (lucide-static@0.468.0). Úsalo solo si ningún icono incluido sirve.
set -e
n="$1"; [ -z "$n" ] && { echo "Uso: add_icon.sh nombre-icono"; exit 1; }
d="$(cd "$(dirname "$0")/../assets/icons" && pwd)"
curl -fsS -m 20 -o "$d/$n.svg" "https://cdn.jsdelivr.net/npm/lucide-static@0.468.0/icons/$n.svg" && echo "añadido: $n" || { rm -f "$d/$n.svg"; echo "no existe en Lucide: $n"; exit 1; }
