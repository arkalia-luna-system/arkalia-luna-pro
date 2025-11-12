#!/bin/bash
# 🔍 Script de Healthcheck Robuste pour Arkalia-LUNA
# Version: 2.8.0
# Description: Vérification complète de la santé des services

set -e

# Configuration
API_BASE_URL="http://localhost:8000"
ASSISTANTIA_URL="http://localhost:8001"
REFLEXIA_URL="http://localhost:8002"
TIMEOUT=10
MAX_RETRIES=3

# Couleurs pour les logs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Fonction de logging
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Fonction de test HTTP avec retry
test_endpoint() {
    local url=$1
    local description=$2
    local retries=0

    while [ $retries -lt $MAX_RETRIES ]; do
        if curl -f -s --max-time $TIMEOUT "$url" > /dev/null 2>&1; then
            log_success "$description: OK"
            return 0
        else
            retries=$((retries + 1))
            if [ $retries -lt $MAX_RETRIES ]; then
                log_warning "$description: Tentative $retries/$MAX_RETRIES échouée, nouvelle tentative dans 2s..."
                sleep 2
            else
                log_error "$description: ÉCHEC après $MAX_RETRIES tentatives"
                return 1
            fi
        fi
    done
}

# Fonction de vérification des métriques système
check_system_metrics() {
    log_info "Vérification des métriques système..."

    # Vérification de la mémoire
    memory_usage=$(free | grep Mem | awk '{printf "%.1f", $3/$2 * 100.0}')
    if (( $(echo "$memory_usage > 90" | bc -l) )); then
        log_warning "Utilisation mémoire élevée: ${memory_usage}%"
    else
        log_success "Mémoire OK: ${memory_usage}%"
    fi

    # Vérification du disque
    disk_usage=$(df / | tail -1 | awk '{print $5}' | sed 's/%//')
    if [ "$disk_usage" -gt 90 ]; then
        log_warning "Utilisation disque élevée: ${disk_usage}%"
    else
        log_success "Disque OK: ${disk_usage}%"
    fi

    # Vérification de la charge CPU
    load_average=$(uptime | awk -F'load average:' '{print $2}' | awk '{print $1}' | sed 's/,//')
    log_info "Charge CPU: $load_average"
}

# Fonction de vérification des processus
check_processes() {
    log_info "Vérification des processus critiques..."

    # Vérification du processus Python principal
    if pgrep -f "scripts.run.run_arkalia_api\|scripts/run/run_arkalia_api.py" > /dev/null; then
        log_success "Processus API principal: ACTIF"
    else
        log_error "Processus API principal: INACTIF"
        return 1
    fi

    # Vérification d'uvicorn
    if pgrep -f "uvicorn" > /dev/null; then
        log_success "Serveur Uvicorn: ACTIF"
    else
        log_warning "Serveur Uvicorn: INACTIF"
    fi
}

# Fonction de vérification des fichiers critiques
check_critical_files() {
    log_info "Vérification des fichiers critiques..."

    critical_files=(
        "/app/scripts/run/run_arkalia_api.py"
        "/app/helloria/core.py"
        "/app/modules/reflexia/core.py"
        "/app/modules/zeroia/core.py"
        "/app/modules/assistantia/core.py"
    )

    for file in "${critical_files[@]}"; do
        if [ -f "$file" ]; then
            log_success "Fichier présent: $file"
        else
            log_error "Fichier manquant: $file"
            return 1
        fi
    done
}

# Fonction de vérification des répertoires
check_directories() {
    log_info "Vérification des répertoires..."

    directories=(
        "/app/logs"
        "/app/state"
        "/app/cache"
        "/app/modules/zeroia/state"
        "/app/modules/assistantia/logs"
    )

    for dir in "${directories[@]}"; do
        if [ -d "$dir" ] && [ -w "$dir" ]; then
            log_success "Répertoire accessible: $dir"
        else
            log_warning "Répertoire problématique: $dir"
        fi
    done
}

# Fonction de vérification des ports
check_ports() {
    log_info "Vérification des ports..."

    # Port 8000 (API principale)
    if netstat -tuln | grep -q ":8000 "; then
        log_success "Port 8000: ÉCOUTE"
    else
        log_error "Port 8000: PAS D'ÉCOUTE"
        return 1
    fi

    # Port 8001 (AssistantIA)
    if netstat -tuln | grep -q ":8001 "; then
        log_success "Port 8001: ÉCOUTE"
    else
        log_warning "Port 8001: PAS D'ÉCOUTE"
    fi

    # Port 8002 (ReflexIA)
    if netstat -tuln | grep -q ":8002 "; then
        log_success "Port 8002: ÉCOUTE"
    else
        log_warning "Port 8002: PAS D'ÉCOUTE"
    fi
}

# Fonction principale de healthcheck
main_healthcheck() {
    log_info "🔍 Début du healthcheck Arkalia-LUNA..."

    local exit_code=0

    # Vérifications de base
    check_critical_files || exit_code=1
    check_directories
    check_processes || exit_code=1
    check_ports || exit_code=1

    # Vérifications HTTP
    log_info "Vérification des endpoints HTTP..."

    test_endpoint "$API_BASE_URL/health" "API Health" || exit_code=1
    test_endpoint "$API_BASE_URL/status" "API Status" || exit_code=1
    test_endpoint "$API_BASE_URL/metrics" "API Metrics" || exit_code=1

    # Vérifications des services dépendants (optionnelles)
    test_endpoint "$ASSISTANTIA_URL/api/v1/health" "AssistantIA Health" || log_warning "AssistantIA non disponible"
    test_endpoint "$REFLEXIA_URL/health" "ReflexIA Health" || log_warning "ReflexIA non disponible"

    # Vérifications système
    check_system_metrics

    # Résumé final
    if [ $exit_code -eq 0 ]; then
        log_success "🎉 Healthcheck COMPLET - Tous les services critiques sont opérationnels"
        echo "OK"
    else
        log_error "❌ Healthcheck ÉCHOUÉ - Certains services critiques sont défaillants"
        echo "FAILED"
    fi

    exit $exit_code
}

# Fonction de healthcheck rapide (pour Docker)
quick_healthcheck() {
    if curl -f -s --max-time 5 "$API_BASE_URL/health" > /dev/null 2>&1; then
        echo "OK"
        exit 0
    else
        echo "FAILED"
        exit 1
    fi
}

# Gestion des arguments
case "${1:-main}" in
    "quick")
        quick_healthcheck
        ;;
    "main"|"full")
        main_healthcheck
        ;;
    "system")
        check_system_metrics
        ;;
    "processes")
        check_processes
        ;;
    "files")
        check_critical_files
        ;;
    "ports")
        check_ports
        ;;
    *)
        echo "Usage: $0 [quick|main|full|system|processes|files|ports]"
        echo "  quick    - Healthcheck rapide pour Docker"
        echo "  main     - Healthcheck complet (défaut)"
        echo "  full     - Healthcheck complet avec diagnostics"
        echo "  system   - Vérification des métriques système uniquement"
        echo "  processes- Vérification des processus uniquement"
        echo "  files    - Vérification des fichiers critiques uniquement"
        echo "  ports    - Vérification des ports uniquement"
        exit 1
        ;;
esac
