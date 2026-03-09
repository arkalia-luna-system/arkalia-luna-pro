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

echo "🐳 Lancement de la stack Docker..."
make run
