#!/bin/bash
# 🔄 Script de restauration de config archivée
# Usage : ./restore_config.sh <nom_du_fichier> [chemin_cible]

set -e

if [ -z "$1" ]; then
  echo "Usage : $0 <nom_du_fichier> [chemin_cible]"
  exit 1
fi

FICHIER="$1"
CIBLE="${2:-.}"
SOURCE="archive/configs/$FICHIER"

if [ ! -f "$SOURCE" ]; then
  echo "❌ Fichier $FICHIER introuvable dans archive/configs/"
  exit 2
fi

cp "$SOURCE" "$CIBLE/"
echo "✅ $FICHIER restauré dans $CIBLE/"
