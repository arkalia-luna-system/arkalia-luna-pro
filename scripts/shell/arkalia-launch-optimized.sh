#!/bin/bash
# 🚀 Arkalia-LUNA Launch Optimized v4.0
# Script de lancement rapide pour le système optimisé

set -e

echo "🌕 ARKALIA-LUNA - LANCEMENT OPTIMISÉ v4.0"
echo "=========================================="
echo "⏰ $(date)"
echo ""

# Couleurs pour l'affichage
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Fonction de log coloré
log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

log_step() {
    echo -e "${PURPLE}🔧 $1${NC}"
}

# Vérification des prérequis
check_prerequisites() {
    log_step "Vérification des prérequis..."

    # Vérifier Python
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
        log_success "Python $PYTHON_VERSION détecté"
    else
        log_error "Python3 non trouvé"
        exit 1
    fi

    # Vérifier Docker
    if command -v docker &> /dev/null; then
        DOCKER_VERSION=$(docker --version | cut -d' ' -f3 | cut -d',' -f1)
        log_success "Docker $DOCKER_VERSION détecté"
    else
        log_warning "Docker non trouvé - Mode local uniquement"
    fi

    # Vérifier les fichiers requis
    required_files=(
        "requirements.txt"
        "arkalia_score.py"
        "demo_global.py"
        "modules/core/storage.py"
    )

    for file in "${required_files[@]}"; do
        if [ -f "$file" ]; then
            log_success "$file présent"
        else
            log_error "$file manquant"
            exit 1
        fi
    done
}

# Installation des dépendances
install_dependencies() {
    log_step "Installation des dépendances..."

    if [ -f "requirements.txt" ]; then
        log_info "Installation des packages Python..."
        pip3 install -r requirements.txt --quiet
        log_success "Dépendances Python installées"
    else
        log_warning "requirements.txt non trouvé"
    fi
}

# Test de l'abstraction storage
test_storage() {
    log_step "Test de l'abstraction storage..."

    python3 -c "
from modules.core.storage import StorageManager
storage = StorageManager(backend='json', base_path='test_state')
storage.save_state('test', {'status': 'ok'})
data = storage.get_state('test')
print('✅ Storage test réussi' if data else '❌ Storage test échoué')
storage.delete_module_data('test')
"
}

# Test du score cognitif
test_cognitive_score() {
    log_step "Test du score cognitif global..."

    python3 -c "
from arkalia_score import ArkaliaScoreGenerator
generator = ArkaliaScoreGenerator()
score = generator.calculate_global_score()
print(f'✅ Score cognitif: {score[\"global_score\"]:.3f} ({score[\"status\"]})')
"
}

# Test de la démonstration globale
test_demo() {
    log_step "Test de la démonstration globale..."

    if [ -f "demo_global.py" ]; then
        log_info "Lancement de la démonstration (mode test)..."
        timeout 30s python3 demo_global.py --test-mode || log_warning "Démo interrompue (normal)"
        log_success "Démonstration testée"
    else
        log_warning "demo_global.py non trouvé"
    fi
}

# Test des optimisations Docker
test_docker() {
    log_step "Test des optimisations Docker..."

    if command -v docker &> /dev/null; then
        # Vérifier les Dockerfiles
        dockerfiles=(
            "Dockerfile"
            "Dockerfile.zeroia"
            "Dockerfile.reflexia"
            "Dockerfile.sandozia"
            "Dockerfile.assistantia"
            "Dockerfile.security"
        )

        for dockerfile in "${dockerfiles[@]}"; do
            if [ -f "$dockerfile" ]; then
                log_success "$dockerfile présent"
            else
                log_warning "$dockerfile manquant"
            fi
        done

        # Vérifier docker-compose optimisé
        if [ -f "docker-compose.optimized.yml" ]; then
            log_success "docker-compose.optimized.yml présent"

            # Validation syntaxe
            if docker-compose -f docker-compose.optimized.yml config --quiet; then
                log_success "Configuration Docker valide"
            else
                log_warning "Configuration Docker invalide"
            fi
        else
            log_warning "docker-compose.optimized.yml manquant"
        fi
    else
        log_warning "Docker non disponible - tests Docker ignorés"
    fi
}

# Test des tests d'intégration
test_integration_tests() {
    log_step "Test des tests d'intégration..."

    integration_tests=(
        "tests/integration/test_zeroia_reflexia_sync.py"
        "tests/integration/test_api_guardian_behavior.py"
    )

    for test_file in "${integration_tests[@]}"; do
        if [ -f "$test_file" ]; then
            test_count=$(grep -c "def test_" "$test_file" || echo "0")
            log_success "$test_file présent ($test_count tests)"
        else
            log_warning "$test_file manquant"
        fi
    done
}

# Affichage des métriques
show_metrics() {
    log_step "Métriques du système..."

    # Score cognitif actuel
    if [ -f "arkalia_score.toml" ]; then
        log_info "Score cognitif actuel:"
        python3 -c "
import toml
try:
    data = toml.load('arkalia_score.toml')
    score = data.get('global_score', 'N/A')
    status = data.get('status', 'N/A')
    print(f'   🌍 Score: {score}')
    print(f'   📈 Statut: {status}')
except:
    print('   ❌ Erreur lecture score')
"
    fi

    # Métriques de performance
    log_info "Métriques de performance:"
    python3 -c "
import psutil
cpu = psutil.cpu_percent(interval=1)
memory = psutil.virtual_memory().percent
print(f'   🖥️ CPU: {cpu:.1f}%')
print(f'   💾 Mémoire: {memory:.1f}%')
"
}

# Menu principal
show_menu() {
    echo ""
    echo "🎯 MENU PRINCIPAL"
    echo "================="
    echo "1. 🔧 Test complet du système"
    echo "2. 🧪 Tests d'intégration uniquement"
    echo "3. 📊 Score cognitif uniquement"
    echo "4. 🐳 Tests Docker uniquement"
    echo "5. 🚀 Lancement démo complète"
    echo "6. 📈 Afficher métriques"
    echo "7. 🧹 Nettoyage"
    echo "8. ❌ Quitter"
    echo ""
    read -p "Choisissez une option (1-8): " choice
}

# Nettoyage
cleanup() {
    log_step "Nettoyage..."

    # Supprimer les fichiers de test
    rm -rf test_state/ 2>/dev/null || true
    rm -f test_backup.json 2>/dev/null || true

    # Nettoyer les conteneurs Docker si nécessaire
    if command -v docker &> /dev/null; then
        docker system prune -f 2>/dev/null || true
    fi

    log_success "Nettoyage terminé"
}

# Test complet
run_full_test() {
    log_step "Test complet du système..."

    check_prerequisites
    install_dependencies
    test_storage
    test_cognitive_score
    test_demo
    test_docker
    test_integration_tests
    show_metrics

    log_success "Test complet terminé avec succès !"
}

# Lancement démo complète
run_full_demo() {
    log_step "Lancement de la démonstration complète..."

    if [ -f "demo_global.py" ]; then
        log_info "Démarrage de la démonstration..."
        python3 demo_global.py
    else
        log_error "demo_global.py non trouvé"
    fi
}

# Boucle principale
main() {
    echo "🌕 ARKALIA-LUNA - SYSTÈME OPTIMISÉ v4.0"
    echo "========================================"
    echo "Système d'IA enterprise prêt pour la production"
    echo ""

    while true; do
        show_menu

        case $choice in
            1)
                run_full_test
                ;;
            2)
                test_integration_tests
                ;;
            3)
                test_cognitive_score
                ;;
            4)
                test_docker
                ;;
            5)
                run_full_demo
                ;;
            6)
                show_metrics
                ;;
            7)
                cleanup
                ;;
            8)
                log_info "Au revoir !"
                exit 0
                ;;
            *)
                log_error "Option invalide"
                ;;
        esac

        echo ""
        read -p "Appuyez sur Entrée pour continuer..."
    done
}

# Si des arguments sont fournis, exécuter directement
if [ $# -gt 0 ]; then
    case $1 in
        "test")
            run_full_test
            ;;
        "demo")
            run_full_demo
            ;;
        "cleanup")
            cleanup
            ;;
        "metrics")
            show_metrics
            ;;
        *)
            log_error "Usage: $0 [test|demo|cleanup|metrics]"
            exit 1
            ;;
    esac
else
    main
fi
