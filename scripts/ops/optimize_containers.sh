#!/bin/bash
# 🚀 Script d'Optimisation Conteneurs Arkalia-LUNA
# Résout tous les problèmes Docker et optimise les performances

set -e

echo "🚀 [OPTIMIZE] Démarrage de l'optimisation des conteneurs Arkalia-LUNA..."

# === Nettoyage des fichiers macOS ===
echo "🧹 [CLEAN] Suppression des fichiers cachés macOS..."
find . -name "._*" -type f -delete 2>/dev/null || true
find . -name ".DS_Store" -type f -delete 2>/dev/null || true

# === Vérification des fichiers requis ===
echo "📋 [CHECK] Vérification des fichiers requis..."
if [ ! -f "requirements.txt" ]; then
    echo "❌ [ERROR] requirements.txt manquant !"
    exit 1
fi

echo "✅ [CHECK] requirements.txt trouvé ($(wc -l < requirements.txt) lignes)"

# === Nettoyage Docker ===
echo "🐳 [DOCKER] Nettoyage du système Docker..."
docker compose down 2>/dev/null || true
docker system prune -f
docker builder prune -f

# === Construction optimisée par étapes ===
echo "🔨 [BUILD] Construction des images optimisées..."

# API Principale d'abord
echo "🌐 [API] Construction Arkalia API..."
if docker compose build --no-cache arkalia-api; then
    echo "✅ [API] Arkalia API construite avec succès"
else
    echo "❌ [API] Échec construction Arkalia API"
    exit 1
fi

# AssistantIA
echo "🤖 [ASSISTANTIA] Construction AssistantIA..."
if docker compose build --no-cache assistantia; then
    echo "✅ [ASSISTANTIA] AssistantIA construite avec succès"
else
    echo "⚠️ [ASSISTANTIA] Échec construction AssistantIA - Continuons..."
fi

# ReflexIA
echo "🔄 [REFLEXIA] Construction ReflexIA..."
if docker compose build --no-cache reflexia; then
    echo "✅ [REFLEXIA] ReflexIA construite avec succès"
else
    echo "⚠️ [REFLEXIA] Échec construction ReflexIA - Continuons..."
fi

# ZeroIA
echo "🧠 [ZEROIA] Construction ZeroIA..."
if docker compose build --no-cache zeroia; then
    echo "✅ [ZEROIA] ZeroIA construite avec succès"
else
    echo "⚠️ [ZEROIA] Échec construction ZeroIA - Continuons..."
fi

# Sandozia
echo "🧬 [SANDOZIA] Construction Sandozia..."
if docker compose build --no-cache sandozia; then
    echo "✅ [SANDOZIA] Sandozia construite avec succès"
else
    echo "⚠️ [SANDOZIA] Échec construction Sandozia - Continuons..."
fi

# === Démarrage des conteneurs ===
echo "🚀 [START] Démarrage des conteneurs optimisés..."
docker compose up -d

# === Vérification santé ===
echo "🏥 [HEALTH] Vérification de la santé des conteneurs..."
sleep 10

docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

# === Statistiques des images ===
echo "📊 [STATS] Tailles des images optimisées :"
docker images | grep arkalia | awk '{print $1 "\t" $7 $8}'

# === Tests de connectivité ===
echo "🔌 [TEST] Tests de connectivité..."
if curl -f http://localhost:8000/health 2>/dev/null; then
    echo "✅ [TEST] API principale accessible"
else
    echo "⚠️ [TEST] API principale non accessible"
fi

if curl -f http://localhost:8001/health 2>/dev/null; then
    echo "✅ [TEST] AssistantIA accessible"
else
    echo "⚠️ [TEST] AssistantIA non accessible"
fi

echo ""
echo "🎉 [SUCCESS] Optimisation des conteneurs terminée !"
echo "📝 [INFO] Utilisez 'docker ps' pour voir l'état des conteneurs"
echo "🔍 [INFO] Utilisez 'docker logs <container>' pour les logs détaillés"
