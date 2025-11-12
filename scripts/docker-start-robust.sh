#!/bin/bash
# 🚀 Script de démarrage Docker robuste pour Arkalia-LUNA
# Gère les dépendances et les healthchecks de manière robuste

set -e

echo "🌕 Démarrage robuste d'Arkalia-LUNA avec Docker Compose..."

# Vérifier que Docker est en cours d'exécution
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker n'est pas en cours d'exécution. Démarrez Docker et réessayez."
    exit 1
fi

# Nettoyer les conteneurs existants
echo "🧹 Nettoyage des conteneurs existants..."
docker-compose -f config/docker/docker-compose-fixed.yml down --remove-orphans

# Créer les répertoires nécessaires
echo "📁 Création des répertoires nécessaires..."
mkdir -p logs state config

# Démarrer les services dans l'ordre correct
echo "🚀 Démarrage des services dans l'ordre..."

# 1. Démarrer l'API principale
echo "📡 Démarrage de l'API principale (arkalia-api)..."
docker-compose -f config/docker/docker-compose-fixed.yml up -d arkalia-api

# Attendre que l'API soit prête
echo "⏳ Attente que l'API principale soit prête..."
timeout=300  # 5 minutes
elapsed=0
while [ $elapsed -lt $timeout ]; do
    if docker-compose -f config/docker/docker-compose-fixed.yml ps arkalia-api | grep -q "healthy"; then
        echo "✅ API principale prête!"
        break
    fi
    echo "⏳ Attente... ($elapsed/$timeout secondes)"
    sleep 10
    elapsed=$((elapsed + 10))
done

if [ $elapsed -ge $timeout ]; then
    echo "❌ Timeout: L'API principale n'est pas prête"
    docker-compose -f config/docker/docker-compose-fixed.yml logs arkalia-api
    exit 1
fi

# 2. Démarrer ReflexIA
echo "🔁 Démarrage de ReflexIA..."
docker-compose -f config/docker/docker-compose-fixed.yml up -d reflexia

# Attendre que ReflexIA soit prêt
echo "⏳ Attente que ReflexIA soit prêt..."
timeout=180  # 3 minutes
elapsed=0
while [ $elapsed -lt $timeout ]; do
    if docker-compose -f config/docker/docker-compose-fixed.yml ps reflexia | grep -q "healthy"; then
        echo "✅ ReflexIA prêt!"
        break
    fi
    echo "⏳ Attente... ($elapsed/$timeout secondes)"
    sleep 10
    elapsed=$((elapsed + 10))
done

if [ $elapsed -ge $timeout ]; then
    echo "❌ Timeout: ReflexIA n'est pas prêt"
    docker-compose -f config/docker/docker-compose-fixed.yml logs reflexia
    exit 1
fi

# 3. Démarrer les autres services
echo "🚀 Démarrage des autres services..."
docker-compose -f config/docker/docker-compose-fixed.yml up -d

# Attendre que tous les services soient prêts
echo "⏳ Attente que tous les services soient prêts..."
timeout=300  # 5 minutes
elapsed=0
while [ $elapsed -lt $timeout ]; do
    unhealthy_count=$(docker-compose -f config/docker/docker-compose-fixed.yml ps | grep -c "unhealthy" || true)
    if [ "$unhealthy_count" -eq 0 ]; then
        echo "✅ Tous les services sont prêts!"
        break
    fi
    echo "⏳ Attente... Services non prêts: $unhealthy_count"
    sleep 15
    elapsed=$((elapsed + 15))
done

# Afficher le statut final
echo "📊 Statut final des services:"
docker-compose -f config/docker/docker-compose-fixed.yml ps

# Vérifier les endpoints
echo "🔍 Vérification des endpoints..."
services=(
    "http://localhost:8000/health"
    "http://localhost:8001/api/v1/health"
    "http://localhost:8002/health"
    "http://localhost:8003/health"
)

for endpoint in "${services[@]}"; do
    if command -v curl > /dev/null 2>&1; then
        if curl -f -s "$endpoint" > /dev/null; then
            echo "✅ $endpoint - OK"
        else
            echo "❌ $endpoint - ÉCHEC"
        fi
    else
        echo "⚠️  curl non disponible, impossible de vérifier $endpoint"
    fi
done

echo "🎉 Démarrage terminé! Arkalia-LUNA est maintenant opérationnel."
echo "📚 Documentation: http://localhost:8000/docs"
echo "🔍 Monitoring: http://localhost:8000/metrics"
