#!/bin/bash

# Alias de compatibilité.
# Script canonique: scripts/ark-vscode-reload.sh

set -euo pipefail

exec "$(dirname "$0")/ark-vscode-reload.sh" "$@"
