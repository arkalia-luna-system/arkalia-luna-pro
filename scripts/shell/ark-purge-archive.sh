#!/bin/bash
set -e

# 🌕 ARKALIA-LUNA - SCRIPT DE SUPPRESSION SÉLECTIVE DES ARCHIVES
# Version : 2.8.1 - Pack Pro
# Date : 4 juillet 2025

# Configuration
LOG_FILE="logs/ark-purge-archive_$(date +%Y%m%d_%H%M%S).log"
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
    echo -e "${PURPLE}🌕 ARKALIA-LUNA - SUPPRESSION SÉLECTIVE DES ARCHIVES${NC}"
    echo -e "${PURPLE}================================================${NC}"
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

# Fonction de suppression des rapports JSON (le plus gros)
purge_json_reports() {
    print_status "🗑️  Suppression des rapports JSON (3.3GB)..."

    if [ -d "archive/json_reports" ]; then
        local size=$(du -sh archive/json_reports | cut -f1)
        print_warning "Suppression de json_reports ($size)"

        if [ $DRY_RUN -eq 0 ]; then
            rm -rf archive/json_reports
            print_success "json_reports supprimé (3.3GB libéré)"
        else
            print_status "DRY RUN: json_reports serait supprimé"
        fi
    fi
}

# Fonction de suppression des archives obsolètes
purge_obsolete_archives() {
    print_status "🗑️  Suppression des archives obsolètes..."

    # Archives de fichiers obsolètes
    for dir in archive/obsolete_files_*; do
        if [ -d "$dir" ]; then
            local size=$(du -sh "$dir" | cut -f1)
            print_warning "Suppression de $dir ($size)"

            if [ $DRY_RUN -eq 0 ]; then
                rm -rf "$dir"
                print_success "$dir supprimé"
            else
                print_status "DRY RUN: $dir serait supprimé"
            fi
        fi
    done

    # Archives manuelles obsolètes
    for dir in archive/obsolete_manual_*; do
        if [ -d "$dir" ]; then
            local size=$(du -sh "$dir" | cut -f1)
            print_warning "Suppression de $dir ($size)"

            if [ $DRY_RUN -eq 0 ]; then
                rm -rf "$dir"
                print_success "$dir supprimé"
            else
                print_status "DRY RUN: $dir serait supprimé"
            fi
        fi
    done

    # Dossier obsolete_files général
    if [ -d "archive/obsolete_files" ]; then
        local size=$(du -sh archive/obsolete_files | cut -f1)
        print_warning "Suppression de obsolete_files ($size)"

        if [ $DRY_RUN -eq 0 ]; then
            rm -rf archive/obsolete_files
            print_success "obsolete_files supprimé"
        else
            print_status "DRY RUN: obsolete_files serait supprimé"
        fi
    fi
}

# Fonction de suppression des tests obsolètes
purge_obsolete_tests() {
    print_status "🗑️  Suppression des tests obsolètes..."

    for dir in archive/tests_*; do
        if [ -d "$dir" ]; then
            local size=$(du -sh "$dir" | cut -f1)
            print_warning "Suppression de $dir ($size)"

            if [ $DRY_RUN -eq 0 ]; then
                rm -rf "$dir"
                print_success "$dir supprimé"
            else
                print_status "DRY RUN: $dir serait supprimé"
            fi
        fi
    done
}

# Fonction de suppression des anciennes archives de nettoyage
purge_old_cleanups() {
    print_status "🗑️  Suppression des anciennes archives de nettoyage..."

    # Garder seulement la plus récente
    local latest_cleanup=$(ls -td archive/cleanup_* 2>/dev/null | head -1)

    for dir in archive/cleanup_*; do
        if [ -d "$dir" ] && [ "$dir" != "$latest_cleanup" ]; then
            local size=$(du -sh "$dir" | cut -f1)
            print_warning "Suppression de $dir ($size) - ancienne archive"

            if [ $DRY_RUN -eq 0 ]; then
                rm -rf "$dir"
                print_success "$dir supprimé"
            else
                print_status "DRY RUN: $dir serait supprimé"
            fi
        fi
    done
}

# Fonction de suppression des fichiers macOS cachés dans archive
purge_macos_files() {
    print_status "🍎 Suppression des fichiers macOS cachés dans archive..."

    find archive -name "._*" -type f | while read -r mac_file; do
        if [ $DRY_RUN -eq 0 ]; then
            rm "$mac_file"
            print_success "$mac_file supprimé"
        else
            print_status "DRY RUN: $mac_file serait supprimé"
        fi
    done
}

# Fonction de suppression des snapshots anciens
purge_old_snapshots() {
    print_status "📸 Suppression des snapshots anciens..."

    if [ -d "archive/snapshots" ]; then
        # Garder seulement les snapshots des 7 derniers jours
        find archive/snapshots -type f -mtime +7 | while read -r snapshot; do
            if [ $DRY_RUN -eq 0 ]; then
                rm "$snapshot"
                print_success "$snapshot supprimé"
            else
                print_status "DRY RUN: $snapshot serait supprimé"
            fi
        done
    fi
}

# Fonction de suppression des logs anciens
purge_old_logs() {
    print_status "📝 Suppression des logs anciens..."

    if [ -d "archive/logs" ]; then
        # Garder seulement les logs des 30 derniers jours
        find archive/logs -type f -mtime +30 | while read -r log; do
            if [ $DRY_RUN -eq 0 ]; then
                rm "$log"
                print_success "$log supprimé"
            else
                print_status "DRY RUN: $log serait supprimé"
            fi
        done
    fi
}

# Fonction de calcul de l'espace libéré
calculate_space_freed() {
    local total_freed=0

    # Calculer l'espace qui sera libéré
    if [ -d "archive/json_reports" ]; then
        local size=$(du -sm archive/json_reports | cut -f1)
        total_freed=$((total_freed + size))
    fi

    for dir in archive/obsolete_files_* archive/obsolete_manual_* archive/tests_*; do
        if [ -d "$dir" ]; then
            local size=$(du -sm "$dir" | cut -f1)
            total_freed=$((total_freed + size))
        fi
    done

    echo "$total_freed"
}

# Fonction d'affichage du résumé
print_summary() {
    local space_freed=$1
    local space_freed_mb=$((space_freed / 1024))

    echo -e "\n${CYAN}===== RÉSUMÉ DE LA SUPPRESSION =====${NC}"
    echo -e "${CYAN}Espace qui sera libéré : ${space_freed}MB (${space_freed_mb}GB)${NC}"
    echo -e "${CYAN}Log détaillé : $LOG_FILE${NC}"
    echo -e "${CYAN}=====================================${NC}\n"
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
            echo "  --force       : Supprime sans demander confirmation"
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
SPACE_TO_FREE_MB=$((SPACE_TO_FREE / 1024))

print_warning "🚨 ATTENTION : Cette opération va supprimer définitivement $SPACE_TO_FREE MB d'archives !"

# Demande de confirmation (sauf si --force)
if [ $FORCE -eq 0 ] && [ $DRY_RUN -eq 0 ]; then
    echo -e "${YELLOW}Êtes-vous sûr de vouloir continuer ? (y/N)${NC}"
    read -r response
    if [[ ! "$response" =~ ^[Yy]$ ]]; then
        print_error "Opération annulée par l'utilisateur"
        exit 1
    fi
fi

# Suppression sélective
purge_json_reports
purge_obsolete_archives
purge_obsolete_tests
purge_old_cleanups
purge_macos_files
purge_old_snapshots
purge_old_logs

# Calcul de l'espace libéré
END_TIME=$(date +%s)
DURATION=$((END_TIME-START_TIME))

# Affichage du résumé
print_summary "$SPACE_TO_FREE"

print_success "🌕 Suppression Arkalia-LUNA terminée avec succès !"
print_status "📊 Archives obsolètes supprimées définitivement"
print_warning "💡 Espace libéré : $SPACE_TO_FREE_MB GB"

exit 0
