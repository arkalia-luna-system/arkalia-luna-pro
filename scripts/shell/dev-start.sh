#!/usr/bin/env bash
set -euo pipefail

# Dev-start Arkalia-LUNA Pro
# - suppose le venv déjà activé
# - lance la stack Docker complète avec Memoria activée

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$REPO_ROOT"

export PYTHONPATH=.
export MEMORIA_ENABLED="true"

echo "🌕 Arkalia-LUNA Pro - dev-start"

echo "🧪 Optionnel: make test-unit (commenté par défaut)"
# make test-unit

echo "🧹 make clean (nettoyage complet des artefacts)..."
make clean || true

echo "🧹 Nettoyage des fichiers AppleDouble à la racine, dans docker/, core/ et scripts/..."
find . -maxdepth 1 -name '._*' -delete || true
find . -maxdepth 1 -name '.__*' -delete || true
find docker -name '._*' -delete || true
find docker -name '.__*' -delete || true
find core -name '._*' -delete || true
find core -name '.__*' -delete || true
find scripts -name '._*' -delete || true
find scripts -name '.__*' -delete || true

echo "🐳 Lancement de la stack Docker..."
make run
