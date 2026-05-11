#!/bin/bash
# 🚀 Script de démarrage - Intelligence Générative Avancée

set -e

echo "🚀 Démarrage de l'Intelligence Générative Avancée..."

# === Vérification de l'environnement ===
if [ "$GENERATIVE_AI_ENABLED" != "true" ]; then
    echo "⚠️  Intelligence Générative désactivée"
    exit 0
fi

# === Création des répertoires ===
mkdir -p /app/logs
mkdir -p /app/modules/generative_ai/state
mkdir -p /app/modules/generative_ai/generated

# === Vérification des dépendances ===
echo "🔍 Vérification des dépendances..."
python -c "import asyncio, json, logging, pathlib; print('✅ Dépendances OK')"

# === Démarrage du module ===
echo "🚀 Lancement de l'Intelligence Générative..."
exec python -m modules.generative_ai.core --mode production --daemon
