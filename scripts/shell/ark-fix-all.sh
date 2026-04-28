#!/bin/bash
# 🚀 Script de correction rapide Arkalia-LUNA
# Raccourci de compatibilité vers le script canonique.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

exec "$PROJECT_ROOT/scripts/ark-fix-linting.sh" "$@"
