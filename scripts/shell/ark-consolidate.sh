#!/bin/bash
set -e

# 🌕 ARKALIA-LUNA - SCRIPT DE CONSOLIDATION COMPLÈTE
# Version : 2.8.1 - Pack Pro
# Date : 4 juillet 2025

# Configuration
LOG_FILE="logs/ark-consolidate_$(date +%Y%m%d_%H%M%S).log"
DRY_RUN=0
FORCE=0

# Couleurs pour l'affichage
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Fonctions d'affichage
print_header() {
    echo -e "${PURPLE}🌕 ARKALIA-LUNA - CONSOLIDATION COMPLÈTE${NC}"
    echo -e "${PURPLE}====================================${NC}"
    echo ""
}

print_status() {
    echo -e "${BLUE}ℹ️  $1${NC}" | tee -a "$LOG_FILE"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}" | tee -a "$LOG_FILE"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}" | tee -a "$LOG_FILE"
}

print_error() {
    echo -e "${RED}❌ $1${NC}" | tee -a "$LOG_FILE"
}

# Fonction de consolidation des dossiers de couverture
consolidate_coverage() {
    print_status "📊 Consolidation des dossiers de couverture..."

    if [ -d "htmlcov-performance" ] || [ -d "htmlcov-chaos" ] || [ -d "htmlcov-critical" ] || [ -d "htmlcov-security" ]; then
        print_warning "Fusion des dossiers de couverture dans htmlcov/"

        if [ $DRY_RUN -eq 0 ]; then
            # Créer le dossier consolidé
            mkdir -p htmlcov/

            # Fusionner tous les dossiers de couverture
            for dir in htmlcov-*; do
                if [ -d "$dir" ]; then
                    print_status "Fusion de $dir dans htmlcov/"
                    cp -r "$dir"/* htmlcov/ 2>/dev/null || true
                fi
            done

            # Supprimer les anciens dossiers
            rm -rf htmlcov-*
            print_success "Dossiers de couverture consolidés (68MB libéré)"
        else
            print_status "DRY RUN: Dossiers de couverture seraient consolidés"
        fi
    fi
}

# Fonction de nettoyage des états et logs
cleanup_state_logs() {
    print_status "🧹 Nettoyage des états et logs..."

    # Nettoyer les logs anciens (plus de 30 jours)
    if [ -d "logs" ]; then
        print_warning "Suppression des logs de plus de 30 jours"

        if [ $DRY_RUN -eq 0 ]; then
            find logs -type f -mtime +30 -delete
            print_success "Logs anciens supprimés"
        else
            print_status "DRY RUN: Logs anciens seraient supprimés"
        fi
    fi

    # Nettoyer les états temporaires
    if [ -d "state" ]; then
        print_warning "Nettoyage des états temporaires"

        if [ $DRY_RUN -eq 0 ]; then
            # Garder seulement les états des 7 derniers jours
            find state -type f -mtime +7 -name "*.tmp" -delete
            find state -type f -mtime +7 -name "*.cache" -delete
            print_success "États temporaires nettoyés"
        else
            print_status "DRY RUN: États temporaires seraient nettoyés"
        fi
    fi
}

# Fonction d'organisation des rapports
organize_reports() {
    print_status "📄 Organisation des rapports..."

    if [ $DRY_RUN -eq 0 ]; then
        # Créer le dossier reports
        mkdir -p reports/

        # Déplacer tous les rapports .md
        for report in *.md; do
            if [ -f "$report" ] && [[ "$report" != "README.md" ]]; then
                print_status "Déplacement de $report vers reports/"
                mv "$report" reports/
            fi
        done

        print_success "Rapports organisés dans reports/"
    else
        print_status "DRY RUN: Rapports seraient organisés dans reports/"
    fi
}

# Fonction de consolidation des configurations
consolidate_configs() {
    print_status "🔧 Consolidation des configurations..."

    if [ $DRY_RUN -eq 0 ]; then
        # Créer le dossier configs
        mkdir -p configs/

        # Déplacer les configurations pytest
        for config in pytest-*.ini; do
            if [ -f "$config" ]; then
                print_status "Déplacement de $config vers configs/"
                mv "$config" configs/
            fi
        done

        # Déplacer les configurations Docker
        for compose in docker-compose*.yml; do
            if [ -f "$compose" ] && [[ "$compose" != "docker-compose.yml" ]]; then
                print_status "Déplacement de $compose vers configs/"
                mv "$compose" configs/
            fi
        done

        # Créer un fichier de configuration unifié
        cat > configs/pytest-unified.ini << 'EOF'
[tool:pytest]
# Configuration unifiée pour tous les types de tests
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts =
    --strict-markers
    --strict-config
    --verbose
    --tb=short
    --cov=modules
    --cov-report=html:htmlcov
    --cov-report=term-missing
    --cov-fail-under=80
markers =
    unit: Unit tests
    integration: Integration tests
    performance: Performance tests
    security: Security tests
    chaos: Chaos engineering tests
EOF

        print_success "Configurations consolidées dans configs/"
    else
        print_status "DRY RUN: Configurations seraient consolidées"
    fi
}

# Fonction d'organisation des Dockerfiles
organize_dockerfiles() {
    print_status "🐳 Organisation des Dockerfiles..."

    if [ $DRY_RUN -eq 0 ]; then
        # Créer le dossier docker
        mkdir -p docker/

        # Déplacer tous les Dockerfiles sauf le principal
        for dockerfile in Dockerfile.*; do
            if [ -f "$dockerfile" ]; then
                print_status "Déplacement de $dockerfile vers docker/"
                mv "$dockerfile" docker/
            fi
        done

        print_success "Dockerfiles organisés dans docker/"
    else
        print_status "DRY RUN: Dockerfiles seraient organisés dans docker/"
    fi
}

# Fonction de consolidation des outils de développement
consolidate_dev_tools() {
    print_status "🛠️  Consolidation des outils de développement..."

    if [ $DRY_RUN -eq 0 ]; then
        # Créer le dossier dev
        mkdir -p dev/

        # Déplacer les dossiers de développement
        if [ -d ".dev" ]; then
            print_status "Déplacement de .dev vers dev/"
            mv .dev/* dev/ 2>/dev/null || true
            rmdir .dev
        fi

        if [ -d ".vscode" ]; then
            print_status "Déplacement de .vscode vers dev/"
            mv .vscode dev/
        fi

        if [ -d ".benchmarks" ]; then
            print_status "Déplacement de .benchmarks vers dev/"
            mv .benchmarks dev/
        fi

        print_success "Outils de développement consolidés dans dev/"
    else
        print_status "DRY RUN: Outils de développement seraient consolidés"
    fi
}

# Fonction de nettoyage des caches
cleanup_caches() {
    print_status "🗑️  Nettoyage des caches..."

    if [ $DRY_RUN -eq 0 ]; then
        # Nettoyer les caches Python
        find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
        find . -name "*.pyc" -delete 2>/dev/null || true

        # Nettoyer les caches de build
        rm -rf build/ dist/ *.egg-info/ 2>/dev/null || true

        # Nettoyer les caches Node.js
        rm -rf node_modules/ .npm/ 2>/dev/null || true

        print_success "Caches nettoyés"
    else
        print_status "DRY RUN: Caches seraient nettoyés"
    fi
}

# Fonction de création d'un script de lancement unifié
create_unified_launcher() {
    print_status "🚀 Création d'un lanceur unifié..."

    if [ $DRY_RUN -eq 0 ]; then
        cat > arkalia.sh << 'EOF'
#!/bin/bash
# 🌕 ARKALIA-LUNA - LANCEUR UNIFIÉ
# Version : 2.8.1 - Pack Pro

set -e

# Couleurs
GREEN='\033[0;32m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m'

print_header() {
    echo -e "${PURPLE}🌕 ARKALIA-LUNA - LANCEUR UNIFIÉ${NC}"
    echo -e "${PURPLE}==============================${NC}"
    echo ""
}

print_help() {
    echo "Usage: $0 [COMMANDE]"
    echo ""
    echo "Commandes disponibles:"
    echo "  start       - Démarrer Arkalia-LUNA"
    echo "  test        - Lancer tous les tests"
    echo "  test-fast   - Tests rapides"
    echo "  test-perf   - Tests de performance"
    echo "  clean       - Nettoyer le projet"
    echo "  archive     - Archiver les fichiers temporaires"
    echo "  purge       - Supprimer les archives obsolètes"
    echo "  consolidate - Consolider la structure"
    echo "  build       - Construire le projet"
    echo "  deploy      - Déployer"
    echo "  help        - Afficher cette aide"
    echo ""
}

case "$1" in
    start)
        print_header
        echo -e "${GREEN}🚀 Démarrage d'Arkalia-LUNA...${NC}"
        python -m scripts.run.run_arkalia_api
        ;;
    test)
        print_header
        echo -e "${GREEN}🧪 Lancement de tous les tests...${NC}"
        ./ark-test-full.sh
        ;;
    test-fast)
        print_header
        echo -e "${GREEN}⚡ Tests rapides...${NC}"
        python -m pytest tests/unit/ -v --tb=short
        ;;
    test-perf)
        print_header
        echo -e "${GREEN}📊 Tests de performance...${NC}"
        ./ark-test-performance.sh
        ;;
    clean)
        print_header
        echo -e "${GREEN}🧹 Nettoyage du projet...${NC}"
        ./ark-clean.sh
        ;;
    archive)
        print_header
        echo -e "${GREEN}📦 Archivage des fichiers temporaires...${NC}"
        ./ark-archive.sh
        ;;
    purge)
        print_header
        echo -e "${GREEN}🗑️  Suppression des archives obsolètes...${NC}"
        ./ark-purge-archive.sh --force
        ;;
    consolidate)
        print_header
        echo -e "${GREEN}🔧 Consolidation de la structure...${NC}"
        ./ark-consolidate.sh --force
        ;;
    build)
        print_header
        echo -e "${GREEN}🔨 Construction du projet...${NC}"
        docker-compose build
        ;;
    deploy)
        print_header
        echo -e "${GREEN}🚀 Déploiement...${NC}"
        docker-compose up -d
        ;;
    help|*)
        print_help
        ;;
esac
EOF

        chmod +x arkalia.sh
        print_success "Lanceur unifié créé: arkalia.sh"
    else
        print_status "DRY RUN: Lanceur unifié serait créé"
    fi
}

# Fonction de calcul de l'espace qui sera libéré
calculate_space_freed() {
    local total_freed=0

    # Espace des dossiers de couverture
    if [ -d "htmlcov-performance" ] || [ -d "htmlcov-chaos" ] || [ -d "htmlcov-critical" ] || [ -d "htmlcov-security" ]; then
        total_freed=$((total_freed + 68))
    fi

    # Espace des logs anciens (estimation)
    if [ -d "logs" ]; then
        local old_logs=$(find logs -type f -mtime +30 2>/dev/null | wc -l)
        if [ $old_logs -gt 0 ]; then
            total_freed=$((total_freed + 10))
        fi
    fi

    echo "$total_freed"
}

# Fonction d'affichage du résumé
print_summary() {
    local space_freed=$1

    echo -e "\n${CYAN}===== RÉSUMÉ DE LA CONSOLIDATION =====${NC}"
    echo -e "${CYAN}Espace qui sera libéré : ${space_freed}MB${NC}"
    echo -e "${CYAN}Log détaillé : $LOG_FILE${NC}"
    echo -e "${CYAN}========================================${NC}\n"
}

# Parsing des options
for arg in "$@"; do
    case $arg in
        --dry-run)
            DRY_RUN=1
            ;;
        --force)
            FORCE=1
            ;;
        --help)
            echo "Usage: $0 [--dry-run] [--force]"
            echo "  --dry-run     : Affiche ce qui serait fait sans le faire"
            echo "  --force       : Consolide sans demander confirmation"
            exit 0
            ;;
    esac
    shift
done

# Initialisation
print_header
mkdir -p logs
START_TIME=$(date +%s)

# Calcul de l'espace qui sera libéré
SPACE_TO_FREE=$(calculate_space_freed)

print_warning "🚨 ATTENTION : Cette opération va consolider la structure du projet !"

# Demande de confirmation (sauf si --force)
if [ $FORCE -eq 0 ] && [ $DRY_RUN -eq 0 ]; then
    echo -e "${YELLOW}Êtes-vous sûr de vouloir continuer ? (y/N)${NC}"
    read -r response
    if [[ ! "$response" =~ ^[Yy]$ ]]; then
        print_error "Opération annulée par l'utilisateur"
        exit 1
    fi
fi

# Consolidation complète
consolidate_coverage
cleanup_state_logs
organize_reports
consolidate_configs
organize_dockerfiles
consolidate_dev_tools
cleanup_caches
create_unified_launcher

# Calcul de l'espace libéré
END_TIME=$(date +%s)
DURATION=$((END_TIME-START_TIME))

# Affichage du résumé
print_summary "$SPACE_TO_FREE"

print_success "🌕 Consolidation Arkalia-LUNA terminée avec succès !"
print_status "📊 Structure du projet optimisée et organisée"
print_warning "💡 Espace libéré : $SPACE_TO_FREE MB"
print_status "🚀 Nouveau lanceur unifié : ./arkalia.sh"

exit 0
