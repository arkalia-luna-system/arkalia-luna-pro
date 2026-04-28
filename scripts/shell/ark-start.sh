#!/bin/bash
# Wrapper de compatibilité: utilise le script de démarrage canonique.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

exec "$PROJECT_ROOT/scripts/ark-docker-start.sh" "$@"
