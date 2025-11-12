#!/bin/bash
# 🚀 Script de démarrage Docker robuste pour Arkalia-LUNA

set -e

echo "🚀 Démarrage d'Arkalia-LUNA avec Docker Compose..."

# Vérifier que Docker est en cours d'exécution
if ! docker info >/dev/null 2>&1; then
    echo "❌ Docker n'est pas en cours d'exécution"
    exit 1
fi

# Nettoyer les conteneurs existants
echo "🧹 Nettoyage des conteneurs existants..."
docker compose down --remove-orphans

# Construire les images
echo "🔨 Construction des images Docker..."
docker compose build --no-cache

# Démarrer les services un par un avec des délais
echo "🚀 Démarrage des services..."

# 1. Démarrer arkalia-api en premier
echo "📡 Démarrage de arkalia-api..."
docker compose up -d arkalia-api

# Attendre que arkalia-api soit healthy
echo "⏳ Attente que arkalia-api soit healthy..."
timeout=180
elapsed=0
while [ $elapsed -lt $timeout ]; do
    if docker compose ps arkalia-api | grep -q "healthy"; then
        echo "✅ arkalia-api est healthy"
        break
    fi
    echo "⏳ arkalia-api en cours de démarrage... ($elapsed/$timeout s)"
    sleep 10
    elapsed=$((elapsed + 10))
done

if [ $elapsed -ge $timeout ]; then
    echo "❌ Timeout: arkalia-api n'est pas devenu healthy"
    docker compose logs arkalia-api
    exit 1
fi

# 2. Démarrer reflexia
echo "🔄 Démarrage de reflexia..."
docker compose up -d reflexia

# Attendre que reflexia soit healthy
echo "⏳ Attente que reflexia soit healthy..."
timeout=120
elapsed=0
while [ $elapsed -lt $timeout ]; do
    if docker compose ps reflexia | grep -q "healthy"; then
        echo "✅ reflexia est healthy"
        break
    fi
    echo "⏳ reflexia en cours de démarrage... ($elapsed/$timeout s)"
    sleep 10
    elapsed=$((elapsed + 10))
done

# 3. Démarrer les autres services
echo "🚀 Démarrage des autres services..."
docker compose up -d

# Attendre que tous les services soient healthy
echo "⏳ Attente que tous les services soient healthy..."
timeout=600
elapsed=0
while [ $elapsed -lt $timeout ]; do
    unhealthy_count=$(docker compose ps | grep -c "unhealthy" || true)
    if [ "$unhealthy_count" -eq 0 ]; then
        echo "✅ Tous les services sont healthy"
        break
    fi
    echo "⏳ Services en cours de démarrage... ($elapsed/$timeout s)"
    docker compose ps
    sleep 20
    elapsed=$((elapsed + 20))
done

if [ $elapsed -ge $timeout ]; then
    echo "❌ Timeout: Certains services ne sont pas devenus healthy"
    docker compose ps
    echo "📋 Logs des services problématiques:"
    docker compose logs --tail=50
    exit 1
fi

# Afficher le statut final
echo "📊 Statut final des services:"
docker-compose ps

echo "🎉 Arkalia-LUNA démarré avec succès!"
echo "🌐 API disponible sur: http://localhost:8000"
echo "🔍 Healthcheck: http://localhost:8000/health"
