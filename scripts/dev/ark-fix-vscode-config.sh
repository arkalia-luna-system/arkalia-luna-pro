#!/bin/bash

# 🌕 Arkalia-LUNA — Fix VSCode/Cursor Configuration
# Corrige les chemins de venv et redémarre l'éditeur

echo "🔧 Correction des configurations VSCode/Cursor..."

# Sauvegarde des paramètres utilisateur Cursor
if [ -f ~/Library/Application\ Support/Cursor/User/settings.json ]; then
    cp ~/Library/Application\ Support/Cursor/User/settings.json ~/Library/Application\ Support/Cursor/User/settings.json.backup.$(date +%Y%m%d_%H%M%S)
    echo "✅ Sauvegarde des paramètres Cursor créée"
fi

# Correction des chemins dans les paramètres utilisateur Cursor
if [ -f ~/Library/Application\ Support/Cursor/User/settings.json ]; then
    sed -i '' 's|/Volumes/T7/arkalia-system|/Volumes/T7/arkalia-luna-venv|g' ~/Library/Application\ Support/Cursor/User/settings.json
    sed -i '' 's|/Volumes/T7/arkalia-luna-venv/shared-venv/bin/python3|/Volumes/T7/arkalia-luna-venv/bin/python|g' ~/Library/Application\ Support/Cursor/User/settings.json
    echo "✅ Paramètres utilisateur Cursor corrigés"
fi

# Vérification du venv
if [ ! -f /Volumes/T7/arkalia-luna-venv/bin/python ]; then
    echo "❌ Erreur : Le venv /Volumes/T7/arkalia-luna-venv n'existe pas"
    echo "💡 Crée le venv avec : python -m venv /Volumes/T7/arkalia-luna-venv"
    exit 1
fi

echo "✅ Vérification du venv : OK"

# Redémarrage de Cursor
echo "🔄 Redémarrage de Cursor..."
pkill -f "Cursor" 2>/dev/null || true
sleep 2

# Ouverture du projet dans Cursor
echo "🚀 Ouverture du projet dans Cursor..."
open -a Cursor /Volumes/T7/devstation/cursor/arkalia-luna-pro

echo "✅ Configuration VSCode/Cursor corrigée et redémarrée"
echo "💡 Si l'erreur persiste, redémarre Cursor manuellement"
