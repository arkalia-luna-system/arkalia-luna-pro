#!/bin/bash
# 🧪 Script de test pour vérifier le healthcheck de l'API Arkalia

echo "🔍 Test du healthcheck de l'API Arkalia..."

# Test de l'endpoint /health
echo "📡 Test de l'endpoint /health..."
response=$(curl -s -f "http://localhost:8000/health" 2>/dev/null)
if [ $? -eq 0 ]; then
    echo "✅ /health accessible: $response"
else
    echo "❌ /health inaccessible"
fi

# Test de l'endpoint /status
echo "📡 Test de l'endpoint /status..."
response=$(curl -s -f "http://localhost:8000/status" 2>/dev/null)
if [ $? -eq 0 ]; then
    echo "✅ /status accessible: $response"
else
    echo "❌ /status inaccessible"
fi

# Test de l'endpoint racine
echo "📡 Test de l'endpoint racine /..."
response=$(curl -s -f "http://localhost:8000/" 2>/dev/null)
if [ $? -eq 0 ]; then
    echo "✅ / accessible: $response"
else
    echo "❌ / inaccessible"
fi

echo "🏁 Test terminé"
