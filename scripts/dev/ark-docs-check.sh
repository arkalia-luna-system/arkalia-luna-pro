#!/bin/bash
# 📚 Script validation automatique documentation Arkalia-LUNA
# Usage: ./scripts/dev/ark-docs-check.sh

set -euo pipefail

echo "📚 VALIDATION DOCUMENTATION ARKALIA-LUNA"
echo "========================================"

# Couleurs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Fonction d'affichage
print_status() {
    local status="$1"
    local message="$2"
    if [ "$status" = "OK" ]; then
        echo -e "${GREEN}✅ $message${NC}"
    elif [ "$status" = "WARNING" ]; then
        echo -e "${YELLOW}⚠️  $message${NC}"
    else
        echo -e "${RED}❌ $message${NC}"
    fi
}

# 1. Vérification structure documentation
echo -e "\n${BLUE}🔍 Vérification structure...${NC}"
REQUIRED_DIRS=(
    "docs/security"
    "docs/modules"
    "docs/infrastructure"
    "docs/releases"
    "docs/fonctionnement"
)

for dir in "${REQUIRED_DIRS[@]}"; do
    if [ -d "$dir" ]; then
        print_status "OK" "Dossier $dir existe"
    else
        print_status "ERROR" "Dossier $dir manquant"
    fi
done

# 2. Vérification fichiers critiques
echo -e "\n${BLUE}📄 Vérification fichiers critiques...${NC}"
REQUIRED_FILES=(
    "docs/index.md"
    "docs/security/SECURITY.md"
    "docs/security/incident-response.md"
    "docs/security/backup-recovery.md"
    "docs/modules/assistantia.md"
    "docs/modules/zeroia.md"
    "docs/releases/CHANGELOG.md"
    "mkdocs.yml"
)

for file in "${REQUIRED_FILES[@]}"; do
    if [ -f "$file" ]; then
        size=$(wc -c < "$file")
        if [ "$size" -gt 100 ]; then
            print_status "OK" "$file ($size bytes)"
        else
            print_status "WARNING" "$file trop petit ($size bytes)"
        fi
    else
        print_status "ERROR" "$file manquant"
    fi
done

# 3. Test build MkDocs
echo -e "\n${BLUE}🏗️  Test build MkDocs...${NC}"
if mkdocs build --quiet > /dev/null 2>&1; then
    print_status "OK" "Build MkDocs réussie"
else
    print_status "ERROR" "Échec build MkDocs"
    echo "Exécutez: mkdocs build --strict pour plus de détails"
fi

# 4. Vérification liens externes
echo -e "\n${BLUE}🔗 Vérification navigation MkDocs...${NC}"
if grep -q "nav:" mkdocs.yml; then
    sections=$(grep -A 50 "nav:" mkdocs.yml | grep -c ":")
    print_status "OK" "Navigation: $sections sections configurées"
else
    print_status "ERROR" "Navigation manquante dans mkdocs.yml"
fi

# 5. Vérification contenu Phase 3
echo -e "\n${BLUE}🛡️  Vérification Phase 3 Sécurité...${NC}"
SECURITY_FILES=(
    "docs/security/SECURITY.md"
    "docs/security/incident-response.md"
    "docs/security/backup-recovery.md"
    "docs/security/penetration-testing.md"
    "docs/security/compliance.md"
    "docs/security/architecture.mmd"
)

security_total=0
for file in "${SECURITY_FILES[@]}"; do
    if [ -f "$file" ]; then
        size=$(wc -c < "$file")
        security_total=$((security_total + size))
    fi
done

if [ "$security_total" -gt 50000 ]; then
    print_status "OK" "Documentation sécurité: ${security_total} bytes"
else
    print_status "WARNING" "Documentation sécurité incomplète: ${security_total} bytes"
fi

# 6. Test serveur local
echo -e "\n${BLUE}🌐 Test serveur documentation...${NC}"
if command -v mkdocs >/dev/null 2>&1; then
    print_status "OK" "MkDocs installé"
    # Tester que le serveur peut démarrer
    timeout 5 mkdocs serve -a 127.0.0.1:9001 > /dev/null 2>&1 &
    sleep 2
    if pgrep -f "mkdocs serve" > /dev/null; then
        print_status "OK" "Serveur de test fonctionnel"
        pkill -f "mkdocs serve"
    else
        print_status "WARNING" "Problème serveur local"
    fi
else
    print_status "ERROR" "MkDocs non installé"
fi

# 7. Résumé final
echo -e "\n${BLUE}📊 RÉSUMÉ AUDIT${NC}"
echo "=========================="

# Calcul taille totale documentation
total_size=$(find docs/ -name "*.md" -o -name "*.mmd" | xargs wc -c | tail -n 1 | awk '{print $1}')
file_count=$(find docs/ -name "*.md" -o -name "*.mmd" | wc -l)

echo "📁 Fichiers documentation: $file_count"
echo "📏 Taille totale: $total_size bytes (~$((total_size/1024))KB)"

if [ "$total_size" -gt 200000 ]; then
    print_status "OK" "Documentation substantielle et complète"
elif [ "$total_size" -gt 100000 ]; then
    print_status "WARNING" "Documentation correcte mais pourrait être étoffée"
else
    print_status "ERROR" "Documentation insuffisante"
fi

# 8. Liens vers déploiement
echo -e "\n${BLUE}🚀 LIENS UTILES${NC}"
echo "=========================="
echo "📖 Documentation locale: http://127.0.0.1:9000"
echo "🌐 Documentation GitHub Pages: https://arkalia-luna-system.github.io/arkalia-luna-pro/"
echo "🔧 Commandes:"
echo "  - Local: mkdocs serve -a 127.0.0.1:9000"
echo "  - Deploy: mkdocs gh-deploy --clean --force"
echo ""

echo "✅ Audit documentation terminé !"
