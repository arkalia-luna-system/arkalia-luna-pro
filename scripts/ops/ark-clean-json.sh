#!/bin/bash
# 🧠 Arkalia-LUNA JSON Cleaner - Script sécurisé
# Nettoie les fichiers JSON massifs sans supprimer les configs importantes

set -e  # Arrêter en cas d'erreur

echo "🧠 Arkalia-LUNA JSON Cleaner"
echo "================================"
echo ""

# Couleurs pour l'affichage
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Fonction pour afficher les messages
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

# Vérifier si on est dans le bon répertoire
if [ ! -f "pyproject.toml" ]; then
    log_error "Ce script doit être exécuté depuis la racine du projet Arkalia-LUNA"
    exit 1
fi

# Mode dry-run par défaut
DRY_RUN=true
if [ "$1" = "--execute" ]; then
    DRY_RUN=false
    log_warning "Mode EXÉCUTION activé - Les fichiers seront déplacés"
else
    log_info "Mode DRY-RUN - Aucun fichier ne sera modifié"
    log_info "Pour exécuter réellement: $0 --execute"
fi

echo ""

# 1. Nettoyer les caches Python
log_info "1. Nettoyage des caches Python..."

if [ "$DRY_RUN" = true ]; then
    echo "   Fichiers qui seraient supprimés:"
    find . -name ".mypy_cache" -type d 2>/dev/null | head -10
    find . -name ".pytest_cache" -type d 2>/dev/null | head -10
    find . -name "__pycache__" -type d 2>/dev/null | head -10
    echo "   ... (et autres caches)"
else
    find . -name ".mypy_cache" -type d -exec rm -rf {} + 2>/dev/null || true
    find . -name ".pytest_cache" -type d -exec rm -rf {} + 2>/dev/null || true
    find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
    log_success "Caches Python nettoyés"
fi

echo ""

# 2. Analyser les fichiers JSON volumineux
log_info "2. Analyse des fichiers JSON volumineux..."

JSON_FILES=$(find . -name "*.json" -type f -not -path "./node_modules/*" -not -path "./archive/*" 2>/dev/null | wc -l)
LARGE_FILES=$(find . -name "*.json" -type f -not -path "./node_modules/*" -not -path "./archive/*" -size +1M 2>/dev/null | wc -l)

echo "   Total fichiers JSON: $JSON_FILES"
echo "   Fichiers > 1MB: $LARGE_FILES"

if [ "$LARGE_FILES" -gt 0 ]; then
    echo "   Top 10 fichiers volumineux:"
    find . -name "*.json" -type f -not -path "./node_modules/*" -not -path "./archive/*" -exec du -h {} + 2>/dev/null | sort -hr | head -10
fi

echo ""

# 3. Identifier les fichiers à archiver
log_info "3. Identification des fichiers à archiver..."

# Fichiers à préserver (ne pas archiver)
PRESERVE_PATTERNS=(
    "package.json"
    "package-lock.json"
    "tsconfig.json"
    "*.schema.json"
    "config/*.json"
    "docs/assets/docs/*.json"
    "*KEEP.json"  # 🪪 Fichiers marqués comme essentiels
)

# Construire la commande find avec exclusions
FIND_CMD="find . -name \"*.json\" -type f -not -path \"./node_modules/*\" -not -path \"./archive/*\""

for pattern in "${PRESERVE_PATTERNS[@]}"; do
    if [[ $pattern == *"*"* ]]; then
        # Pattern avec wildcard
        FIND_CMD="$FIND_CMD -not -name \"${pattern}\""
    else
        # Pattern simple
        FIND_CMD="$FIND_CMD -not -path \"./$pattern\""
    fi
done

# 🕰️ Ajouter le filtre par ancienneté (15 jours)
FIND_CMD="$FIND_CMD -mtime +15"

# Compter les fichiers à archiver
ARCHIVE_COUNT=$(eval $FIND_CMD 2>/dev/null | wc -l)

echo "   Fichiers à archiver (plus de 15 jours): $ARCHIVE_COUNT"

if [ "$ARCHIVE_COUNT" -gt 0 ]; then
    echo "   Exemples de fichiers à archiver:"
    eval $FIND_CMD 2>/dev/null | head -10
fi

echo ""

# 4. Archiver les fichiers JSON
if [ "$ARCHIVE_COUNT" -gt 0 ]; then
    log_info "4. Archivage des fichiers JSON..."

    if [ "$DRY_RUN" = true ]; then
        echo "   Les fichiers suivants seraient archivés:"
        eval $FIND_CMD 2>/dev/null | head -20
        echo "   ... (et $((ARCHIVE_COUNT - 20)) autres fichiers)"
    else
        # Créer le dossier d'archivage s'il n'existe pas
        mkdir -p archive/json_reports

        # Créer le dossier de logs s'il n'existe pas
        mkdir -p logs

        # Compteur de fichiers archivés
        ARCHIVED_COUNT=0

        # Archiver les fichiers
        eval $FIND_CMD 2>/dev/null | while read -r file; do
            if [ -f "$file" ]; then
                # ⚠️ Vérifier si c'est un fichier essentiel (KEEP.json)
                if [[ "$file" == *KEEP.json ]]; then
                    echo "⏩ Fichier essentiel ignoré : $file"
                    continue
                fi

                # Créer la structure de dossiers dans l'archive
                dir_path=$(dirname "$file" | sed 's|^\./||')
                mkdir -p "archive/json_reports/$dir_path"

                # Déplacer le fichier
                mv "$file" "archive/json_reports/$file"
                echo "   Archivé: $file"
                ((ARCHIVED_COUNT++))
            fi
        done

        # 🪪 Générer le rapport de nettoyage
        echo "🧹 Nettoyage du $(date)" >> logs/json_clean_report.log
        echo "→ $ARCHIVED_COUNT fichiers archivés." >> logs/json_clean_report.log
        echo "→ Critères: fichiers JSON > 15 jours, hors fichiers essentiels" >> logs/json_clean_report.log
        echo "---" >> logs/json_clean_report.log

        log_success "Archivage terminé"
    fi
else
    log_success "Aucun fichier JSON à archiver"
fi

echo ""

# 5. Résumé final
log_info "5. Résumé final..."

if [ "$DRY_RUN" = true ]; then
    echo "   Mode DRY-RUN - Aucune action effectuée"
    echo "   Pour exécuter: $0 --execute"
else
    REMAINING_JSON=$(find . -name "*.json" -type f -not -path "./node_modules/*" -not -path "./archive/*" 2>/dev/null | wc -l)
    echo "   Fichiers JSON restants: $REMAINING_JSON"

    if [ -d "archive/json_reports" ]; then
        ARCHIVED_COUNT=$(find archive/json_reports -name "*.json" -type f 2>/dev/null | wc -l)
        echo "   Fichiers archivés: $ARCHIVED_COUNT"
    fi

    # Afficher le log récent
    if [ -f "logs/json_clean_report.log" ]; then
        echo ""
        echo "📋 Derniers nettoyages:"
        tail -5 logs/json_clean_report.log
    fi
fi

echo ""
log_success "Nettoyage terminé ! 🧠"
echo ""
echo "💡 Prochaines étapes:"
echo "   - Vérifier que tout fonctionne correctement"
echo "   - Commiter les changements du .gitignore"
echo "   - Mettre en place une rotation automatique"
echo ""
echo "🪪 Pour marquer un fichier comme essentiel:"
echo "   mv fichier.json fichierKEEP.json"
