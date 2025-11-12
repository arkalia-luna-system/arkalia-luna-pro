#!/bin/bash
set -e

# 🌕 ARKALIA-LUNA - SCRIPT D'ARCHIVAGE SÉLECTIF
# Version : 2.8.1 - Pack Pro
# Date : 4 juillet 2025

# Configuration
ARCHIVE_DIR="archive/cleanup_$(date +%Y%m%d_%H%M%S)"
LOG_FILE="logs/ark-archive_$(date +%Y%m%d_%H%M%S).log"
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
    echo -e "${PURPLE}🌕 ARKALIA-LUNA - ARCHIVAGE SÉLECTIF${NC}"
    echo -e "${PURPLE}==================================${NC}"
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

# Fonction d'archivage des gros caches
archive_large_caches() {
    print_status "🗂️  Archivage des gros caches..."

    # .mypy_cache (665MB)
    if [ -d ".mypy_cache" ]; then
        if [ $DRY_RUN -eq 0 ]; then
            mv .mypy_cache "$ARCHIVE_DIR/"
        fi
        print_success ".mypy_cache archivé (665MB)"
    fi

    # htmlcov (46MB)
    if [ -d "htmlcov" ]; then
        if [ $DRY_RUN -eq 0 ]; then
            mv htmlcov "$ARCHIVE_DIR/"
        fi
        print_success "htmlcov archivé (46MB)"
    fi

    # .pytest_cache (1.9MB)
    if [ -d ".pytest_cache" ]; then
        if [ $DRY_RUN -eq 0 ]; then
            mv .pytest_cache "$ARCHIVE_DIR/"
        fi
        print_success ".pytest_cache archivé (1.9MB)"
    fi

    print_success "Gros caches archivés"
}

# Fonction d'archivage des caches Python
archive_python_caches() {
    print_status "🐍 Archivage des caches Python..."

    # Cache racine
    if [ -d "__pycache__" ]; then
        if [ $DRY_RUN -eq 0 ]; then
            mv __pycache__ "$ARCHIVE_DIR/"
        fi
        print_success "__pycache__ archivé"
    fi

    # Caches dans les modules
    find . -type d -name "__pycache__" | while read -r cache_dir; do
        if [ $DRY_RUN -eq 0 ]; then
            mkdir -p "$ARCHIVE_DIR/$(dirname "$cache_dir")"
            mv "$cache_dir" "$ARCHIVE_DIR/$(dirname "$cache_dir")/"
        fi
        print_success "$cache_dir archivé"
    done

    print_success "Caches Python archivés"
}

# Fonction d'archivage des fichiers macOS
archive_macos_files() {
    print_status "🍎 Archivage des fichiers macOS..."

    # Fichiers cachés macOS
    find . -name "._*" -type f | while read -r mac_file; do
        if [ $DRY_RUN -eq 0 ]; then
            mkdir -p "$ARCHIVE_DIR/$(dirname "$mac_file")"
            mv "$mac_file" "$ARCHIVE_DIR/$(dirname "$mac_file")/"
        fi
        print_success "$mac_file archivé"
    done

    print_success "Fichiers macOS archivés"
}

# Fonction d'archivage des rapports temporaires
archive_temp_reports() {
    print_status "📊 Archivage des rapports temporaires..."

    # Fichiers de métriques
    for file in demo_results.json chaos_metric_*.toml; do
        if [ -f "$file" ]; then
            if [ $DRY_RUN -eq 0 ]; then
                mv "$file" "$ARCHIVE_DIR/"
            fi
            print_success "$file archivé"
        fi
    done

    # Fichiers de couverture
    for file in .coverage ._.coverage; do
        if [ -f "$file" ]; then
            if [ $DRY_RUN -eq 0 ]; then
                mv "$file" "$ARCHIVE_DIR/"
            fi
            print_success "$file archivé"
        fi
    done

    print_success "Rapports temporaires archivés"
}

# Fonction d'archivage des dossiers de cache
archive_cache_dirs() {
    print_status "📁 Archivage des dossiers de cache..."

    # Cache global
    if [ -d "cache" ] && [ "$(ls -A cache)" ]; then
        if [ $DRY_RUN -eq 0 ]; then
            mv cache "$ARCHIVE_DIR/"
        fi
        print_success "cache archivé (1.3MB)"
    fi

    # Temp
    if [ -d "temp" ] && [ "$(ls -A temp)" ]; then
        if [ $DRY_RUN -eq 0 ]; then
            mv temp "$ARCHIVE_DIR/"
        fi
        print_success "temp archivé (128KB)"
    fi

    # Demo state
    if [ -d "demo_sandozia_state" ] && [ "$(ls -A demo_sandozia_state)" ]; then
        if [ $DRY_RUN -eq 0 ]; then
            mv demo_sandozia_state "$ARCHIVE_DIR/"
        fi
        print_success "demo_sandozia_state archivé (128KB)"
    fi

    print_success "Dossiers de cache archivés"
}

# Fonction d'archivage des logs anciens
archive_old_logs() {
    print_status "📝 Archivage des logs anciens..."

    # Logs de plus de 7 jours
    find . -name "*.log" -mtime +7 | while read -r log_file; do
        if [ $DRY_RUN -eq 0 ]; then
            mkdir -p "$ARCHIVE_DIR/$(dirname "$log_file")"
            mv "$log_file" "$ARCHIVE_DIR/$(dirname "$log_file")/"
        fi
        print_success "$log_file archivé"
    done

    print_success "Logs anciens archivés"
}

# Fonction d'archivage agressif (optionnel)
archive_aggressive() {
    if [ $AGGRESSIVE -eq 1 ]; then
        print_warning "🧹 Archivage agressif activé..."

        # Fichiers de test temporaires
        find . -name "test_*.tmp" -o -name "*_test_*.py" | while read -r test_file; do
            if [ $DRY_RUN -eq 0 ]; then
                mkdir -p "$ARCHIVE_DIR/$(dirname "$test_file")"
                mv "$test_file" "$ARCHIVE_DIR/$(dirname "$test_file")/"
            fi
            print_success "$test_file archivé"
        done

        # Archives anciennes (plus de 30 jours)
        if [ -d "archive" ]; then
            find archive -type d -name "*_obsolete_*" -mtime +30 | while read -r old_archive; do
                if [ $DRY_RUN -eq 0 ]; then
                    mv "$old_archive" "$ARCHIVE_DIR/"
                fi
                print_success "$old_archive archivé"
            done
        fi

        print_success "Archivage agressif terminé"
    fi
}

# Fonction de calcul de l'espace libéré
calculate_space_freed() {
    if [ -d "$ARCHIVE_DIR" ]; then
        local space_freed=$(du -sh "$ARCHIVE_DIR" | cut -f1)
        echo "$space_freed"
    else
        echo "0B"
    fi
}

# Fonction d'affichage du résumé
print_summary() {
    local space_freed=$1
    echo -e "\n${CYAN}===== RÉSUMÉ DE L'ARCHIVAGE =====${NC}"
    echo -e "${CYAN}Espace libéré : $space_freed${NC}"
    echo -e "${CYAN}Archive créée : $ARCHIVE_DIR${NC}"
    echo -e "${CYAN}Log détaillé : $LOG_FILE${NC}"
    echo -e "${CYAN}===============================${NC}\n"
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
            echo "  --aggressive  : Archivage plus agressif (supprime plus de fichiers)"
            exit 0
            ;;
    esac
    shift
done

# Initialisation
print_header
mkdir -p logs
mkdir -p "$ARCHIVE_DIR"
START_TIME=$(date +%s)

# Archivage principal
archive_large_caches
archive_python_caches
archive_macos_files
archive_temp_reports
archive_cache_dirs
archive_old_logs
archive_aggressive

# Calcul de l'espace libéré
END_TIME=$(date +%s)
DURATION=$((END_TIME-START_TIME))
SPACE_FREED=$(calculate_space_freed)

# Affichage du résumé
print_summary "$SPACE_FREED"

print_success "🌕 Archivage Arkalia-LUNA terminé avec succès !"
print_status "📊 Projet nettoyé et optimisé"
print_warning "💡 Pour restaurer : mv $ARCHIVE_DIR/* ."

exit 0
