#!/bin/bash
# 🚀 Lancement Docker persistant pour Arkalia-LUNA

echo "🌕 Lancement de Arkalia-LUNA (mode Docker persisté)..."

docker run -it --rm \
  -v "$(pwd)/logs:/app/logs" \
  -v "$(pwd)/state:/app/state" \
  -p 8000:8000 \
  arkalia-luna
