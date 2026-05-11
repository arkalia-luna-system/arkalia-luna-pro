#!/bin/bash
set -e
for file in state/*.toml; do
  if [ ! -s "$file" ]; then
    echo "⚠️ Fichier vide ou absent: $file"
    cp backups/latest_state_backup.tar.gz state/
    echo "✅ Restauration effectuée."
  fi
done
