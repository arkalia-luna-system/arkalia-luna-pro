#!/bin/bash
# 🚀 Script de démarrage Docker ultra-robuste pour Arkalia-LUNA
# Gère les problèmes de healthcheck avec des stratégies avancées

set -e

echo "🌕 Démarrage ultra-robuste d'Arkalia-LUNA avec Docker Compose..."
echo "🔧 Stratégie : Healthchecks simplifiés + Timeouts étendus + Démarrage séquentiel"

# Vérifier que Docker est en cours d'exécution
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker n'est pas en cours d'exécution. Démarrez Docker et réessayez."
    exit 1
fi

# Nettoyer les conteneurs existants
echo "🧹 Nettoyage des conteneurs existants..."
docker-compose -f docker-compose-ultra-robust.yml down --remove-orphans

# Créer les répertoires nécessaires
echo "📁 Création des répertoires nécessaires..."
mkdir -p logs state config

# Fonction pour attendre qu'un service soit prêt
wait_for_service() {
    local service_name=$1
    local timeout=$2
    local health_check_type=$3

    echo "⏳ Attente que $service_name soit prêt (timeout: ${timeout}s)..."

    elapsed=0
    while [ $elapsed -lt $timeout ]; do
        # Vérifier le statut du conteneur
        container_status=$(docker-compose -f docker-compose-ultra-robust.yml ps $service_name | grep -o "healthy\|unhealthy\|starting" | head -1 || echo "unknown")

        if [ "$container_status" = "healthy" ]; then
            echo "✅ $service_name est prêt!"
            return 0
        elif [ "$container_status" = "unhealthy" ]; then
            echo "❌ $service_name est marqué comme unhealthy"
            # Afficher les logs pour diagnostic
            echo "📋 Logs de $service_name:"
            docker-compose -f docker-compose-ultra-robust.yml logs --tail=20 $service_name
            return 1
        fi

        echo "⏳ Attente... ($elapsed/$timeout secondes) - Status: $container_status"
        sleep 15
        elapsed=$((elapsed + 15))
    done

    echo "⏰ Timeout: $service_name n'est pas prêt après ${timeout}s"
    echo "📋 Logs de $service_name:"
    docker-compose -f docker-compose-ultra-robust.yml logs --tail=50 $service_name
    return 1
}

# Fonction pour tester manuellement un endpoint
test_endpoint() {
    local service_name=$1
    local port=$2
    local endpoint=$3

    echo "🔍 Test manuel de $service_name sur le port $port..."

    # Attendre un peu que le service démarre
    sleep 10

    # Test avec curl si disponible
    if command -v curl > /dev/null 2>&1; then
        if curl -f -s "http://localhost:$port$endpoint" > /dev/null 2>&1; then
            echo "✅ $service_name répond sur le port $port"
            return 0
        else
            echo "❌ $service_name ne répond pas sur le port $port"
            return 1
        fi
    else
        # Test avec Python si curl n'est pas disponible
        if python3 -c "import socket; s=socket.socket(); s.connect(('localhost', $port)); s.close(); print('OK')" 2>/dev/null; then
            echo "✅ $service_name écoute sur le port $port"
            return 0
        else
            echo "❌ $service_name n'écoute pas sur le port $port"
            return 1
        fi
    fi
}

# Démarrage séquentiel avec gestion d'erreurs robuste
echo "🚀 Démarrage des services dans l'ordre avec gestion d'erreurs..."

# 1. Démarrer l'API principale
echo "📡 Démarrage de l'API principale (arkalia-api)..."
docker-compose -f docker-compose-ultra-robust.yml up -d arkalia-api

# Attendre que l'API soit prête (timeout très long)
if wait_for_service "arkalia-api" 600 "healthcheck"; then
    echo "✅ API principale prête!"
else
    echo "⚠️ API principale pas encore prête, test manuel..."
    if test_endpoint "arkalia-api" 8000 "/health"; then
        echo "✅ API principale répond manuellement!"
    else
        echo "❌ API principale ne répond pas, arrêt du processus"
        docker-compose -f docker-compose-ultra-robust.yml logs arkalia-api
        exit 1
    fi
fi

# 2. Démarrer ReflexIA
echo "🔁 Démarrage de ReflexIA..."
docker-compose -f docker-compose-ultra-robust.yml up -d reflexia

# Attendre que ReflexIA soit prêt
if wait_for_service "reflexia" 300 "healthcheck"; then
    echo "✅ ReflexIA prêt!"
else
    echo "⚠️ ReflexIA pas encore prêt, test manuel..."
    if test_endpoint "reflexia" 8002 "/health"; then
        echo "✅ ReflexIA répond manuellement!"
    else
        echo "❌ ReflexIA ne répond pas, arrêt du processus"
        docker-compose -f docker-compose-ultra-robust.yml logs reflexia
        exit 1
    fi
fi

# 3. Démarrer les autres services
echo "🚀 Démarrage des autres services..."
docker-compose -f docker-compose-ultra-robust.yml up -d

# Attendre que tous les services soient prêts
echo "⏳ Attente que tous les services soient prêts..."
timeout=600  # 10 minutes
elapsed=0
while [ $elapsed -lt $timeout ]; do
    unhealthy_count=$(docker-compose -f docker-compose-ultra-robust.yml ps | grep -c "unhealthy" || true)
    starting_count=$(docker-compose -f docker-compose-ultra-robust.yml ps | grep -c "starting" || true)

    if [ "$unhealthy_count" -eq 0 ] && [ "$starting_count" -eq 0 ]; then
        echo "✅ Tous les services sont prêts!"
        break
    fi

    echo "⏳ Attente... Services non prêts: unhealthy=$unhealthy_count, starting=$starting_count"
    sleep 30
    elapsed=$((elapsed + 30))
done

# Afficher le statut final
echo "📊 Statut final des services:"
docker-compose -f docker-compose-ultra-robust.yml ps

# Vérification manuelle des endpoints
echo "🔍 Vérification manuelle des endpoints..."
services=(
    "arkalia-api:8000:/health"
    "arkalia-assistantia:8001:/api/v1/health"
    "reflexia:8002:/health"
    "cognitive:8003:/health"
)

all_services_ok=true
for service_info in "${services[@]}"; do
    IFS=':' read -r service_name port endpoint <<< "$service_info"

    if test_endpoint "$service_name" "$port" "$endpoint"; then
        echo "✅ $service_name - OK"
    else
        echo "❌ $service_name - ÉCHEC"
        all_services_ok=false
    fi
done

# Résumé final
echo ""
echo "🎯 Résumé du démarrage:"
if [ "$all_services_ok" = true ]; then
    echo "🎉 SUCCÈS: Tous les services sont opérationnels!"
    echo "📚 Documentation: http://localhost:8000/docs"
    echo "🔍 Monitoring: http://localhost:8000/metrics"
    echo "🤖 AssistantIA: http://localhost:8001"
    echo "🔁 ReflexIA: http://localhost:8002"
    echo "🧠 Cognitive: http://localhost:8003"
else
    echo "⚠️ ATTENTION: Certains services ne répondent pas correctement"
    echo "📋 Consultez les logs pour plus de détails:"
    echo "   docker-compose -f docker-compose-ultra-robust.yml logs"
fi

echo ""
echo "🔧 Commandes utiles:"
echo "   docker-compose -f docker-compose-ultra-robust.yml ps"
echo "   docker-compose -f docker-compose-ultra-robust.yml logs -f <service>"
echo "   docker-compose -f docker-compose-ultra-robust.yml restart <service>"
