#!/bin/bash
# 🧪 Script de test pour vérifier le healthcheck de l'API Arkalia

set -e

echo "🔍 Test du healthcheck de l'API Arkalia..."

# Fonction de test d'endpoint
test_endpoint() {
    local url=$1
    local name=$2
    echo "📡 Test de l'endpoint $name..."

    if response=$(curl -s -f "$url" 2>/dev/null); then
        echo "✅ $name accessible: $response"
        return 0
    else
        echo "❌ $name inaccessible"
        return 1
    fi
}

# Tests des endpoints principaux
test_endpoint "http://localhost:8000/health" "/health"
test_endpoint "http://localhost:8000/status" "/status"
test_endpoint "http://localhost:8000/" "/ (racine)"

# Tests des services additionnels
echo ""
echo "🔍 Test des services additionnels..."

# Test AssistantIA
if test_endpoint "http://localhost:8001/api/v1/health" "AssistantIA /api/v1/health"; then
    echo "✅ Service AssistantIA accessible"
else
    echo "⚠️ Service AssistantIA non accessible"
fi

# Test ReflexIA
if test_endpoint "http://localhost:8002/health" "ReflexIA /health"; then
    echo "✅ Service ReflexIA accessible"
else
    echo "⚠️ Service ReflexIA non accessible"
fi

# Test Cognitive Reactor
if test_endpoint "http://localhost:8003/health" "Cognitive Reactor /health"; then
    echo "✅ Service Cognitive Reactor accessible"
else
    echo "⚠️ Service Cognitive Reactor non accessible"
fi

echo ""
echo "🏁 Test terminé"
