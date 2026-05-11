#!/bin/bash
# 🔁 Rebuild et relance propre de l’environnement Docker d’Arkalia

set -e  # Stoppe si erreur
PROJECT_ROOT="/Volumes/T7/devstation/cursor/arkalia-luna-pro"

echo "🌑 [ARK-DKR] Nettoyage des fichiers système invisibles..."
find "$PROJECT_ROOT" -name '._*' -delete
find "$PROJECT_ROOT" -name '.DS_Store' -delete

echo "🧹 [ARK-DKR] Arrêt des conteneurs Docker..."
cd "$PROJECT_ROOT"
docker-compose down --remove-orphans

echo "🔧 [ARK-DKR] Rebuild complet de l'image Docker (sans cache)..."
docker-compose build --no-cache

echo "🚀 [ARK-DKR] Redémarrage du conteneur Arkalia-LUNA..."
docker-compose up
