#!/bin/bash
set -e

# 🌕 ARKALIA-LUNA - SCRIPT DE NETTOYAGE ULTRA-PERFORMANT
# Version : 2.8.1 - Pack Pro
# Date : 4 juillet 2025

# Configuration
BACKUP_DIR="backup/cleanup_$(date +%Y%m%d_%H%M%S)"
LOG_FILE="logs/ark-clean_$(date +%Y%m%d_%H%M%S).log"
DRY_RUN=0
AGGRESSIVE=0

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
    echo -e "${PURPLE}🌕 ARKALIA-LUNA - NETTOYAGE ULTRA-PERFORMANT${NC}"
    echo -e "${PURPLE}==========================================${NC}"
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

# Fonction de sauvegarde sélective
backup_important_files() {
    print_status "📦 Sauvegarde des fichiers importants..."
    mkdir -p "$BACKUP_DIR"

    # Sauvegarder les fichiers de config critiques
    if [ -f "config/core_config.json" ]; then
        cp "config/core_config.json" "$BACKUP_DIR/"
    fi
    if [ -f "arkalia_score.toml" ]; then
        cp "arkalia_score.toml" "$BACKUP_DIR/"
    fi
    if [ -f "version.toml" ]; then
        cp "version.toml" "$BACKUP_DIR/"
    fi

    print_success "Sauvegarde terminée dans $BACKUP_DIR"
}

# Fonction de nettoyage des caches Python
clean_python_caches() {
    print_status "🐍 Nettoyage des caches Python..."

    # Caches Python
    find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
    find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
    find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
    find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
    find . -name "*.pyc" -delete 2>/dev/null || true
    find . -name "*.pyo" -delete 2>/dev/null || true
    find . -name "*.pyd" -delete 2>/dev/null || true

    # Fichiers de couverture (PRÉSERVÉS pour la couverture de tests)
    # find . -name ".coverage*" -delete 2>/dev/null || true
    # find . -name "coverage.xml" -delete 2>/dev/null || true
    # find . -name "htmlcov" -type d -exec rm -rf {} + 2>/dev/null || true
    print_warning "Fichiers de couverture préservés pour maintenir la couverture de tests"

    print_success "Caches Python nettoyés"
}

# Fonction de nettoyage des fichiers macOS
clean_macos_files() {
    print_status "🍎 Nettoyage des fichiers macOS..."

    # Fichiers cachés macOS
    find . -name "._*" -delete 2>/dev/null || true
    find . -name ".DS_Store" -delete 2>/dev/null || true
    find . -name "Thumbs.db" -delete 2>/dev/null || true

    print_success "Fichiers macOS nettoyés"
}

# Fonction de nettoyage des artefacts de build
clean_build_artifacts() {
    print_status "🔨 Nettoyage des artefacts de build..."

    # Node.js
    if [ -d "node_modules" ]; then
        rm -rf node_modules
        print_success "node_modules supprimé"
    fi
    if [ -f "package-lock.json" ]; then
        rm -f package-lock.json
        print_success "package-lock.json supprimé"
    fi

    # Python
    find . -name "*.egg-info" -type d -exec rm -rf {} + 2>/dev/null || true
    find . -name "dist" -type d -exec rm -rf {} + 2>/dev/null || true
    find . -name "build" -type d -exec rm -rf {} + 2>/dev/null || true

    # Docker
    find . -name ".dockerignore" -delete 2>/dev/null || true

    print_success "Artefacts de build nettoyés"
}

# Fonction de nettoyage des logs et états
clean_logs_and_states() {
    print_status "📝 Nettoyage des logs et états..."

    # Logs
    if [ -d "logs" ]; then
        find logs -name "*.log" -mtime +7 -delete 2>/dev/null || true
        print_success "Logs anciens nettoyés"
    fi

    # États temporaires
    if [ -d "temp" ]; then
        rm -rf temp/*
        print_success "Dossier temp nettoyé"
    fi

    # Cache global
    if [ -d "cache" ]; then
        rm -rf cache/*
        print_success "Cache global nettoyé"
    fi

    # États de démo
    if [ -d "demo_sandozia_state" ]; then
        rm -rf demo_sandozia_state/*
        print_success "États de démo nettoyés"
    fi

    print_success "Logs et états nettoyés"
}

# Fonction de nettoyage des rapports de test
clean_test_reports() {
    print_status "🧪 Nettoyage des rapports de test..."

    # Rapports de test
    if [ -d "tests/reports" ]; then
        find tests/reports -name "*.log" -mtime +3 -delete 2>/dev/null || true
        find tests/reports -name "*.md" -mtime +3 -delete 2>/dev/null || true
        print_success "Rapports de test anciens nettoyés"
    fi

    # Benchmarks
    if [ -d ".benchmarks" ]; then
        rm -rf .benchmarks/*
        print_success "Benchmarks nettoyés"
    fi

    print_success "Rapports de test nettoyés"
}

# Fonction de nettoyage agressif (optionnel)
clean_aggressive() {
    if [ $AGGRESSIVE -eq 1 ]; then
        print_warning "🧹 Nettoyage agressif activé..."

        # Supprimer tous les fichiers de métriques temporaires
        find . -name "chaos_metric_*.toml" -delete 2>/dev/null || true
        find . -name "demo_results.json" -delete 2>/dev/null || true

        # Nettoyer les backups anciens
        if [ -d "backup" ]; then
            find backup -type d -name "cleanup_*" -mtime +7 -exec rm -rf {} + 2>/dev/null || true
            print_success "Backups anciens supprimés"
        fi

        # Nettoyer les archives anciennes
        if [ -d "archive" ]; then
            find archive -type d -name "*_obsolete_*" -mtime +30 -exec rm -rf {} + 2>/dev/null || true
            print_success "Archives anciennes supprimées"
        fi

        print_success "Nettoyage agressif terminé"
    fi
}

# Fonction d'optimisation de l'espace disque
optimize_disk_space() {
    print_status "💾 Optimisation de l'espace disque..."

    # Vider la corbeille (macOS)
    if command -v osascript &>/dev/null; then
        osascript -e 'tell application "Finder" to empty trash' 2>/dev/null || true
        print_success "Corbeille vidée"
    fi

    # Nettoyer les caches système (si possible)
    if command -v brew &>/dev/null; then
        brew cleanup 2>/dev/null || true
        print_success "Cache Homebrew nettoyé"
    fi

    print_success "Optimisation disque terminée"
}

# Fonction de restauration des fichiers importants
restore_important_files() {
    print_status "🔄 Restauration des fichiers importants..."

    if [ -d "$BACKUP_DIR" ]; then
        if [ -f "$BACKUP_DIR/core_config.json" ]; then
            cp "$BACKUP_DIR/core_config.json" "config/" 2>/dev/null || true
        fi
        if [ -f "$BACKUP_DIR/arkalia_score.toml" ]; then
            cp "$BACKUP_DIR/arkalia_score.toml" . 2>/dev/null || true
        fi
        if [ -f "$BACKUP_DIR/version.toml" ]; then
            cp "$BACKUP_DIR/version.toml" . 2>/dev/null || true
        fi
        print_success "Fichiers importants restaurés"
    fi
}

# Fonction d'affichage du résumé
print_summary() {
    local freed_space=$1
    echo -e "\n${CYAN}===== RÉSUMÉ DU NETTOYAGE =====${NC}"
    echo -e "${CYAN}Espace libéré : $freed_space${NC}"
    echo -e "${CYAN}Log détaillé : $LOG_FILE${NC}"
    echo -e "${CYAN}Backup : $BACKUP_DIR${NC}"
    echo -e "${CYAN}==============================${NC}\n"
}

# Parsing des options
for arg in "$@"; do
    case $arg in
        --dry-run)
            DRY_RUN=1
            ;;
        --aggressive)
            AGGRESSIVE=1
            ;;
        --help)
            echo "Usage: $0 [--dry-run] [--aggressive]"
            echo "  --dry-run     : Affiche ce qui serait fait sans le faire"
            echo "  --aggressive  : Nettoyage plus agressif (supprime plus de fichiers)"
            exit 0
            ;;
    esac
    shift
done

# Initialisation
print_header
mkdir -p logs
START_TIME=$(date +%s)

# Sauvegarde préventive
backup_important_files

# Nettoyage principal
clean_python_caches
clean_macos_files
clean_build_artifacts
clean_logs_and_states
clean_test_reports
clean_aggressive
optimize_disk_space

# Restauration des fichiers importants
restore_important_files

# Calcul de l'espace libéré
END_TIME=$(date +%s)
DURATION=$((END_TIME-START_TIME))

# Affichage du résumé
print_summary "$DURATION secondes"

print_success "🌕 Nettoyage Arkalia-LUNA terminé avec succès !"
print_status "📊 Projet prêt pour une nouvelle session de développement"

exit 0
